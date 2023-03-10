import os
import sys
import subprocess

from libauto.utils.logger import LogWarning
from libauto.core.event import Event
from libauto.core.runtime import registerOp

if sys.platform == "darwin":
    from Foundation import NSAppleScript
    from AppKit import NSNotificationCenter


def formatScript(script, options):
    kwargs = {
        "myPanel": "Accessibility",
        "myPanelID": "com.apple.preference.universalaccess",
        "myAnchor": "Dictation"
    }
    return script.format(**options)


def executeAppleScript(content):
    if sys.platform == "darwin":
        script = NSAppleScript.alloc().initWithSource_(content)
        result, error = script.executeAndReturnError_(None)
        if error is not None:
            LogWarning(f"(OS_SHELL) applescript execution error. {error}")

@registerOp
async def OS_SHELL(ctx, command: str = "", ret: str = ""):
    # if command.endswith("applescript"):
    #     base = os.path.dirname(ctx.yaml_src)
    #     location = os.path.join(base, command)
    #     if not os.path.exists(location):
    #         raise RuntimeError(f"applescript file not found: {location}")
    #     content = open(location, "r").read()
    #     executeAppleScript(content)
    # else:

    if command.endswith("applescript"):
        base = os.path.dirname(ctx.yaml_src)
        absPath = os.path.join(base, command).strip().replace(" ", "\\ ")
        command = f"osascript {absPath}"

    out = subprocess.check_output(command, shell=True)
    if isinstance(out, bytes):
        out = out.decode("utf-8")
    if ret:
        ctx.cache[ret] = out.rstrip('\r\n')
    await ctx.set_next_op()
