import re
import asyncio
from collections.abc import Iterable

from libauto.core.runtime import registerOp
from libauto.core.event import Event


@registerOp
async def CMD_LABEL(ctx, msg: str = ""):
    ctx.log_info(f"executor at label \"{msg}\"")
    await ctx.set_next_op(time=0.01)


@registerOp
async def CMD_FOREACH(ctx, vals: str = "", ret: str = ""):
    if ctx.active_loop.head() != ctx.pc:
        if isinstance(vals, (str, int)):
            vals = [_ for _ in range(int(vals))]
        if not isinstance(vals, Iterable):
            ctx.log_error(f"invalid type for foreach: {type(vals)}")

        # Set up iterators when first time entering the loop
        ctx.active_loop.enter_loop(ctx.pc, vals)

    # get next value from generator
    offset = 1
    index, val = ctx.active_loop.next_val()

    # cache key for index and loopVar
    ret_index, ret_val = ret.split("|")

    if val is None:
        offset = ctx.active_loop.tail() - ctx.pc + 1
        ctx.active_loop.leave_loop()
    else:
        ctx.cache[ret_index] = index
        ctx.cache[ret_val] = val

    await ctx.set_next_op(offset, time=0.01)


@registerOp
async def CMD_RETURN(ctx):
    origin = ctx.pc_callers.pop()
    offset = origin - ctx.pc + 1
    await ctx.set_next_op(offset, time=0.01)


@registerOp
async def CMD_ENDFOR(ctx):
    offset = ctx.active_loop.head() - ctx.pc
    await ctx.set_next_op(offset, time=0.01)


@registerOp
async def CMD_NOTIFY(ctx, title: str = "", content: str = "", params=dict()):
    event = Event.new(Event.O_EVENT_USER_NOTIFY, args={
                      "title": title, "content": content, **params})

    await ctx.send_event_to_ts(event)
    await ctx.set_next_op(time=0.01)


@registerOp
async def CMD_SLEEP(ctx, duration: str = "0s"):
    time_in_sec = float(duration.rstrip("s"))
    await asyncio.sleep(time_in_sec)
    await ctx.set_next_op()


@registerOp
async def CMD_GOTO(ctx, label: str = "", condition: str = "true"):
    offset = 1
    if condition:
        if re.match("^this(\+|-)\d+$", label):
            offset = int(label.replace("this", ""))
        else:
            assert label in ctx.op_label_map, ctx.op_label_map
            offset = ctx.op_label_map[label] - ctx.pc
        ctx.log_warning(f"CMD_GOTO. going to {label}")

    await ctx.set_next_op(offset)


@registerOp
async def CMD_PRINT(ctx, val: str = "", ret: str = ""):
    if not ret:
        ctx.log_warning(f"CMD_PRINT: {val}")
    else:
        ctx.cache[ret] = val
    await ctx.set_next_op()
