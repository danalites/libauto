
from libauto.keyboard.ops import CMD_PRESS, CMD_TYPE, CMD_PRESS, KEY_WAIT, MOUSE_TO, MOUSE_CLICK, MOUSE_SCROLL, EVENT_ON, EVENT_SEND, EVENT_WAIT

from libauto.system.ops import OS_SHELL
from libauto.data.ops import DATA_READ, DATA_PARSE, DATA_UPDATE
from libauto.web.ops import (WEB_CLICK, WEB_UTILS, WEB_HTTP,
                             WEB_INIT, WEB_OPEN, WEB_FIND, WEB_TYPE, WEB_GET, WEB_WAIT)

from libauto.window.ops import WINDOW_FIND, WINDOW_IS_ACTIVE, WINDOW_OCR, USER_INPUT, WINDOW_ENTER, WINDOW_EXIT, WINDOW_WAIT, WINDOW_ANNOTATE

from libauto.store.ops import STORE_SET, STORE_GET, DB_INIT
from libauto.cmd.ops import (CMD_RETURN, CMD_GOTO, CMD_SLEEP, CMD_FOREACH, CMD_NOTIFY, CMD_ENDFOR, CMD_LABEL, CMD_PRINT)

# Mapping from ops to functions
opsTable = {
    # 1. Flow control ops
    "cmd.goto": CMD_GOTO,
    "cmd.for_each": CMD_FOREACH,
    "cmd.end_for": CMD_ENDFOR,
    "cmd.sleep": CMD_SLEEP,
    "user.notify": CMD_NOTIFY,
    "cmd.label": CMD_LABEL,
    "cmd.print": CMD_PRINT,
    "cmd.return": CMD_RETURN,

    # 2. Keyboard and mouse ops
    "key.press": CMD_PRESS,
    "key.type": CMD_TYPE,
    "key.wait": KEY_WAIT,
    "mouse.move": MOUSE_TO,
    "mouse.click": MOUSE_CLICK,
    "mouse.scroll": MOUSE_SCROLL,

    # 3. Event ops
    "event.on": EVENT_ON,
    "event.wait": EVENT_WAIT,
    "event.send": EVENT_SEND,

    # database ops (persistent store)
    "db.init": DB_INIT,
    "db.read": STORE_GET,
    "db.write": STORE_SET,

    # web (browser) ops
    "web.init": WEB_INIT,
    "web.open": WEB_OPEN,
    "web.find": WEB_FIND,
    "web.click": WEB_CLICK,
    "web.type": WEB_TYPE,
    "web.utils": WEB_UTILS,
    "web.get": WEB_GET,
    "web.http": WEB_HTTP,
    "web.wait": WEB_WAIT,

    # os (operating system) ops
    "os.shell": OS_SHELL,

    # data operations (on objects/str)
    "data.read": DATA_READ,
    "data.update": DATA_UPDATE,
    "data.parse": DATA_PARSE,

    # window ops
    "window.wait": WINDOW_WAIT,
    "window.find": WINDOW_FIND,
    "window.ocr": WINDOW_OCR,
    "window.annotate": WINDOW_ANNOTATE,
    "window.is": WINDOW_ENTER,
    "window.exit": WINDOW_EXIT,
    "window.is_active": WINDOW_IS_ACTIVE,
    "user.input": USER_INPUT,
}
