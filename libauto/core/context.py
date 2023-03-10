import re
import os
import copy
import asyncio
import logging
from collections import deque

from .task import Task, loadTask
from .runtime import registerOp, evalExpr

from libauto.ops import opsTable
from libauto.utils.logger import LogInfo, LogError, LogWarning
from libauto.utils.user import getUserHome


def setupLogger(name, logFile, level=logging.WARNING):
    handler = logging.FileHandler(logFile)
    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-8.8s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


@registerOp
async def CMD_CALL(ctx, fn: str, new_inputs: dict = {}):
    if not fn.endswith(("yaml", "yml")):
        # 1. Internal function call
        ctx.pc_callers.append(ctx.pc)
        ctx.cache["arg"] = new_inputs
        offset = ctx.op_label_map[fn] - ctx.pc
        await ctx.set_next_op(offset)

    else:
        # 2. External caller scripts
        base = os.path.dirname(ctx.yaml_src)
        fname = fn if fn.endswith("yaml") else fn + ".yaml"
        location = os.path.join(base, fname)
        if not os.path.exists(location):
            raise RuntimeError(f"(error) CMD.call {location} not found")

        task = loadTask(location)
        if new_inputs:
            for index, val in new_inputs.items():
                task.inputs[index] = val
        await executeOps(task, session=ctx.web_session)
        await ctx.set_next_op()


class ActiveLoopFSM:
    def __init__(self, loops):
        self.loops = loops
        self.curr_loop = -1
        self.loop_vals_generators = deque()

        self.curr_loop_head = None
        self.curr_loop_tail = None

    def head(self):
        return self.curr_loop_head

    def tail(self):
        return self.curr_loop_tail

    def find_loops(self, head):
        for index, loop in enumerate(self.loops):
            if loop[0] == head:
                return index, loop[0], loop[1]

    def enter_loop(self, new_loop_head_pc, vals):
        loop, head, tail = self.find_loops(new_loop_head_pc)
        self.curr_loop = loop
        self.curr_loop_head = head
        self.curr_loop_tail = tail

        def generator(values):
            is_dict = isinstance(values, dict)
            for i, val in enumerate(values):
                ret = {val, values[val]} if is_dict else val
                yield i, ret

        self.loop_vals_generators.append(
            self.LoopValsGen([loop, head, tail], generator(vals))
        )

    def next_val(self):
        gen = self.loop_vals_generators[-1].gen
        try:
            return next(gen)
        except StopIteration:
            return -1, None

    def leave_loop(self):
        del self.loop_vals_generators[-1]
        prev_loop, prev_head, prev_tail = -1, None, None
        try:
            prev_loop, prev_head, prev_tail = \
                self.loop_vals_generators[-1].loop_head_tail
        except:
            pass
        self.curr_loop = prev_loop
        self.curr_loop_head = prev_head
        self.curr_loop_tail = prev_tail

    class LoopValsGen:
        def __init__(self, loop_head_tail, gen):
            self.loop_head_tail = loop_head_tail
            self.gen = gen


# State management
counter = 0


def opSeqNormalize(ops):
    # Convert dictionary struct to list
    new_ops = list()
    global counter
    for op in ops:
        if isinstance(op, dict):
            for k, v in op.items():
                new_ops.append(k)

                label = None
                if k.startswith("cmd.if"):
                    counter += 1
                    label = f"LABEL{counter}"
                    cond = k.lstrip("cmd.if(").rstrip(")").strip()
                    cond = cond.replace("{", "").replace("}", "")
                    new_ops[-1] = f"cmd.goto({label}, " + \
                        "{{not (" + f"{cond}" + ")}})"

                elif k.startswith("cmd.fn"):
                    counter += 1
                    label = f"LABEL{counter}"
                    fn = k.lstrip("cmd.fn(").rstrip(")").strip()
                    new_ops[-1] = f"cmd.goto({label})"
                    new_ops.append(f"cmd.label({fn})")
                
                elif k.startswith("cmd.while"):
                    counter += 1
                    label = f"LABEL{counter}"
                    cond = k.lstrip("cmd.while(").rstrip(")").strip()
                    cond = cond.replace("{", "").replace("}", "")

                    new_ops[-1] = f"cmd.label(WHILE_{label})"
                    new_ops.append(f"cmd.goto({label}, " + \
                        "{{not (" + f"{cond}" + ")}})")

                # Normalize ops in dict.value
                sub_ops = opSeqNormalize(v)
                for n in sub_ops:
                    new_ops.append(n)

                # Append ending ops
                if k.startswith("cmd.for_each"):
                    new_ops.append("cmd.end_for()")

                elif k.startswith("event.on"):
                    new_ops.append("cmd.end_event()")

                elif k.startswith("cmd.if"):
                    new_ops.append(f"cmd.label({label})")

                elif k.startswith("window.is"):
                    new_ops.append(f"window.exit()")

                elif k.startswith("cmd.fn"):
                    new_ops.append("cmd.return()")
                    new_ops.append(f"cmd.label({label})")
                
                elif k.startswith("cmd.while"):
                    new_ops.append(f"cmd.goto(WHILE_{label})")
                    new_ops.append(f"cmd.label({label})")
        else:
            new_ops.append(op)
    return new_ops


def opPreprocess(ops, ctx):
    print("\n")
    LogInfo("======= CMD ops preprocessing =======")
    ops = opSeqNormalize(ops)

    # Extract event regions
    events = dict()
    for index, op in enumerate(ops):
        if op.startswith("event.on"):
            event_name = re.findall(r"event.on\((\w+)\)", op)[0]
            events[event_name] = [index, None]
        elif op.startswith("cmd.end_event"):
            for k, v in events.items():
                if v[1] is None:
                    events[k][1] = index
                    break
    for k, v in events.items():
        s, e = v
        ctx.events[k] = ops[s+1:e]
        del ops[s+1:e+1]

    # Register cmd.label and foreach loops
    ctx.ops = ops
    num_ops = len(ops)
    loop_start_indices = deque()
    loops = list()
    for idx, op in enumerate(ops):
        matched = re.match("^cmd\.label\((.*)\)$", op)
        if matched:
            name = matched.group(1)
            LogInfo(
                f"Context: register label \"{name}\" at {idx}/{num_ops} ")
            ctx.op_label_map[name] = idx

        if op.startswith("cmd.for_each"):
            loop_start_indices.append(idx)

        if op.startswith("cmd.end_for"):
            start = loop_start_indices.pop()
            loops.append((start, idx))

    print(ops)
    LogInfo("======= CMD ops preprocessing END =======\n")
    if events:
        LogInfo("======= CMD ops preprocessing Events =======")
        print(ctx.events)

    ctx.active_loop = ActiveLoopFSM(loops)


def parseRetVal(op, ctx):
    # 1. Op with return vals
    #   inst(args, ...) => $ret0, $ret1, ...
    delim = "=>"
    ret_keys = list()

    if delim in op:
        op, ret = op.split(delim)
        ret_keys = re.findall("\$(\w+)", ret)
        if len(ret_keys) < 1:
            raise RuntimeError(f"(Context) no retKey found in \"{ret}\"")

    # 2. Op with chained action as a ret value (syntactic sugar)
    if op.startswith("web.find"):
        op = op.strip()
        pattern = "(\.type\(.*\)|\.click\(\)|\.screenshot\(.*\)|\.select\(.*\)|\.get\(.*\))$"
        matched = re.findall(pattern, op)

        if matched:
            reserved_ret_key = matched[0]
            op = op.replace(reserved_ret_key, "")

            if reserved_ret_key.startswith(".type"):
                content = reserved_ret_key.lstrip(".type(").rstrip(")")
                content = evalExpr(content, ctx)
                reserved_ret_key = f".type({content})"

            ret_keys.append(reserved_ret_key)

    return op, ret_keys


async def parseOpArgs(opStr, ctx):
    op = opStr.replace("\n", "")
    LogInfo(f"Context: parsing inst: {op}")
    op, ret_keys = parseRetVal(op, ctx)

    inst, op_body = op.split("(", 1)

    # 1. Parse args by "," delimiter (escape with "\,")
    op_body = op_body.strip().rstrip(")")
    args = list()
    for item in op_body.split(","):
        item = item.strip()
        if len(args) > 0:
            if args[-1].endswith("\\"):
                args[-1] = args[-1].rstrip("\\") + "," + item
                continue
        args.append(item)

    # E.x. key.listen({{[1,2,3]}}, EVENT_NAME)
    args_conn = list()
    stack = list()
    for arg in args:
        if "{{" in arg:
            if not "}}" in arg:
                stack.append(arg)
            else:
                args_conn.append(arg)
        elif "}}" in arg:
            if len(stack) == 0:
                raise RuntimeError(f"invalid arg: {arg}")
            stack.append(arg)
            args_conn.append(",".join(stack))
            stack.clear()

        else:
            if len(stack) > 0:
                stack.append(arg)
            else:
                args_conn.append(arg)
    args = args_conn

    # 2. Legality checking
    try:
        func_ptr = CMD_CALL if inst == "cmd.call" else opsTable[inst]
    except Exception as e:
        raise RuntimeError(f"(Context) unknown operation: \"{inst}\"")

    argnames = func_ptr.argnames
    if "ctx" in argnames:
        argnames.remove("ctx")
    kwarg = copy.deepcopy(func_ptr.defaults)

    if len(ret_keys) > 0:
        kwarg["ret"] = "|".join(ret_keys)
    kwarg["ctx"] = ctx

    # 3. Map passed-in args to kwargs
    for arg in args:
        arg_with_prefix = False
        for prefix in argnames:
            if arg.startswith(prefix + "="):
                val = arg.lstrip(prefix + "=")
                kwarg[prefix] = val
                arg_with_prefix = True
                break

        # Ignore undefined keyword arguments
        if not arg_with_prefix:
            if re.findall("^([A-Za-z0-9_-]+)\s*=", arg):
                keys = kwarg.keys()
                LogWarning(
                    f"Context: invalid key in \"{arg}\". Supported optional keys: {keys}")
                continue

            # arg with no prefix; assign to default keys in order
            index = args.index(arg)
            if len(argnames) > index:
                argname = argnames[index]
                kwarg[argname] = arg

    # 4. Evaluate passed in arguments
    for k, v in kwarg.items():
        if k == "ctx":
            continue
        kwarg[k] = evalExpr(v, ctx)

    LogInfo(f"Context: evaluated op \"{inst}\" = {kwarg}")
    return func_ptr, kwarg


class ExeContext(object):
    def __init__(self, task):
        self.task = task

        # Task information
        self.inputs = task.inputs
        self.ops = task.ops
        self.yaml_src = task.source
        self.events = dict()

        # Task logger
        txt = getUserHome(f"logs/{self.task.name}.txt")
        self.logger = setupLogger(self.task.name, txt)

        # Web and window states
        self.web_session = None
        self.web_cookies = None
        self.window = None

        # Task states (PC, loop, cache)
        self.op_label_map = dict()
        self.pc_callers = list()
        self.cache = dict()
        if task.cache:
            self.cache = task.cache
        self.pc = 0
        self.active_loop = None

        # Execution parameters
        self.op_wait_timeout = task.configs.get("op_wait_timeout", 3)
        self.op_interval = task.configs.get("op_interval", 0.05)

        # Callbacks to top-level ts
        self.ts_event_channel_out = None

    def __repr__(self):
        return f"Context({self.task.name},{self.task.uuid})"

    def next(self):
        return self.ops[self.pc]

    async def set_next_op(self, offset=1, time=0):
        self.pc += offset
        interval = time if time > 0 else self.op_interval
        await asyncio.sleep(interval)

    def set_web_session(self, session):
        self.web_session = session

    def set_ts_event_channel(self, channel):
        self.ts_event_channel_out = channel

    async def send_event_to_ts(self, event):
        event.update({"uuid": self.task.uuid, "taskName": self.task.name})
        return await self.ts_event_channel_out(event)

    def log_info(self, msg):
        self.logger.info(msg)
        LogInfo(msg)

    def log_warning(self, msg):
        self.logger.warn(msg)
        LogWarning(msg)

    def log_error(self, msg):
        self.logger.error(msg)
        LogError(msg)

# https://stackoverflow.com/a/61360215
# monitoring tasks are well suited for cooperative scheduling


async def executeOps(task: Task, session=None, event_channel=None):
    # called when trigger conditions are satisfied
    ctx = ExeContext(task)
    opPreprocess(ctx.ops, ctx)

    if session is not None:
        ctx.set_web_session(session)

    if event_channel is not None:
        ctx.set_ts_event_channel(event_channel)

    while ctx.pc < len(ctx.ops):
        op = ctx.next()
        func_ptr, kwargs = await parseOpArgs(op, ctx)
        await func_ptr(**kwargs)
