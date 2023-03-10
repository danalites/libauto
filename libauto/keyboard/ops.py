import sys
import pygb
import pyperclip

from libauto.core.runtime import registerOp
from libauto.core.event import Event


@registerOp
async def CMD_PRESS(ctx, val: str = ""):
    keys = val.split("+")
    ctx.log_warning(f"CMD_KEY pressed {keys}")
    pygb.hotkey(*keys, interval=0.1)
    await ctx.set_next_op()


@registerOp
async def CMD_TYPE(ctx, text: str, epilogue: str = ""):
    pyperclip.copy(text)
    if sys.platform == "darwin":
        pygb.hotkey('Command', 'v', interval=0.1)
    elif sys.platform == "win32":
        pygb.hotkey('Ctrl', 'v', interval=0.1)

    if epilogue:
        keys = epilogue.split("+")
        pygb.hotkey(*keys, interval=0.05)
    await ctx.set_next_op()


@registerOp
async def KEY_WAIT(ctx, value: str = ""):
    event = Event.new(Event.O_EVENT_HOOK_REQ, args={
                      "type": "keyWait", "key": value})
    ret = await ctx.send_event_to_ts(event)
    ctx.log_warning(f"KEY_WAIT: \"{ret}\" resolved. Continue...")
    await ctx.set_next_op()


@registerOp
async def EVENT_WAIT(ctx, event_name: str = "", ret: str = ""):
    event = Event.new(Event.O_EVENT_TASK_EVENT_REQ, args={
        "type": "eventWait",
        "eventName": event_name,
        "argsName": ret,
    })
    await ctx.send_event_to_ts(event)
    await ctx.set_next_op()


@registerOp
async def EVENT_ON(ctx, event_name: str = "", ret: str = ""):
    # Example: event.on(__KEY_PRESSED, {{ {...} }})
    event = Event.new(Event.O_EVENT_EVENT_REQ, args={
        "type": "eventRegister",
        "eventName": event_name,
        "argsName": ret,
        "taskOps": ctx.events[event_name],
    })
    await ctx.send_event_to_ts(event)
    await ctx.set_next_op()


@registerOp
async def EVENT_SEND(ctx, event_name: str = "", args=dict()):
    # Invoke all subtasks associated with the events
    event = Event.new(Event.O_EVENT_EVENT_REQ,
                      args={"eventName": event_name, "args": args})
    await ctx.send_event_to_ts(event)
    await ctx.set_next_op()


@registerOp
async def MOUSE_TO(ctx, pos, options=dict()):
    if isinstance(pos, tuple):
        pos = [pos]

    origin = [0, 0]
    if ctx.window is not None:
        ctx.log_warning(f"MOUSE_TO: {pos} inside {ctx.window}")
        origin = ctx.window.lt

    for p in pos:
        x, y = p
        x = origin[0] + x
        y = origin[1] + y
        pygb.moveTo(x, y)

    await ctx.set_next_op()


@registerOp
async def MOUSE_CLICK(ctx, pos, options=dict()):
    origin = [0, 0]
    if len(pos) == 4:
        x0, y0, w, h = pos
        pos = (x0 + w / 2, y0 + h / 2)

    if ctx.window is not None:
        ctx.log_warning(f"MOUSE_CLICK: {pos} inside {ctx.window}")
        origin = ctx.window.lt

    # TODO: intra window option
    x = origin[0] + pos[0]
    y = origin[1] + pos[1]
    pygb.moveTo(x, y)
    pygb.click()
    await ctx.set_next_op()


@registerOp
async def MOUSE_SCROLL(ctx, offset):
    pygb.scroll(offset)
    await ctx.set_next_op()
