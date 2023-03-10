# coding: utf-8
from libauto.utils.logger import LogWarning

import sys
import time
import pygb
import subprocess


if sys.platform == "darwin":
    from AppKit import NSWorkspace

    # https://stackoverflow.com/a/65766428
    # NSWorkspace.sharedWorkspace().runningApplications()
    # NSWorkspace.sharedWorkspace().frontmostApplication()
    # app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)

    from AppKit import NSApplicationActivateIgnoringOtherApps
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
        kCGNullWindowID
    )
elif sys.platform == "win32":
    from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect


class WindowInstance:
    def __init__(self, pid: int = 0, position: tuple = (0, 0),
                 dimX: int = 0, dimY: int = 0, app: str = "", title: str = ""):
        self.pid = pid
        self.lt = position
        self.wh = (dimX, dimY)
        self.owner = app
        self.title = title

    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __repr__(self):
        return f"WindowInstance(pid={self.pid}, lt={self.lt}, wh={self.wh}, owner={self.owner}, title={self.title})"

def getOpenWindow(name):
    if sys.platform == "darwin":
        options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

        wi = None
        for window in windowList:
            pid = window['kCGWindowOwnerPID']
            windowNumber = window['kCGWindowNumber']
            ownerName = window['kCGWindowOwnerName']
            geometry = window['kCGWindowBounds']
            windowTitle = window.get('kCGWindowName', u'Unknown')

            if name in ownerName:
                title = windowTitle.encode('ascii', 'ignore')
                h, w, x, y = geometry["Height"], geometry["Width"], geometry["X"], geometry["Y"]
                if wi is None or (h > 100 and w > 100):
                    wi = WindowInstance(pid, (x, y), w, h, ownerName, title)
                    if h > 100 and w > 100:
                        return wi
        
        if wi is None:
            opened_apps = set([ app['kCGWindowOwnerName'] for app in windowList ])
            LogWarning(f"Window '{name}' not found. Opened apps: {opened_apps}")

    elif sys.platform == "win32":
        hwnd = GetForegroundWindow()
        title = GetWindowText(hwnd)
        x1, y1, x2, y2 = GetWindowRect(hwnd)
        wi = WindowInstance(hwnd, (x1, y1), x2-x1, y2-y1, title, "")

    return wi

def getActiveWindow():
    # https://stackoverflow.com/a/44229825
    # https://github.com/asweigart/PyGetWindow
    if sys.platform == "darwin":
        curr_app = NSWorkspace.sharedWorkspace().frontmostApplication()
        curr_pid = NSWorkspace.sharedWorkspace().activeApplication()[
            'NSApplicationProcessIdentifier']
        curr_app_name = curr_app.localizedName()

        options = kCGWindowListOptionOnScreenOnly 
        windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

        wi = None
        for window in windowList:
            pid = window['kCGWindowOwnerPID']
            windowNumber = window['kCGWindowNumber']
            ownerName = window['kCGWindowOwnerName']
            geometry = window['kCGWindowBounds']
            windowTitle = window.get('kCGWindowName', u'Unknown')

            if curr_pid == pid:
                title = windowTitle.encode('ascii', 'ignore')
                h, w, x, y = geometry["Height"], geometry["Width"], geometry["X"], geometry["Y"]
                new_wi = WindowInstance(pid, (x, y), w, h, ownerName, title)
                ow, oh = new_wi.wh
                if ow > 100 or oh > 100:
                    wi = new_wi

    elif sys.platform == "win32":
        hwnd = GetForegroundWindow()
        title = GetWindowText(hwnd)
        x1, y1, x2, y2 = GetWindowRect(hwnd)
        wi = WindowInstance(hwnd, (x1, y1), x2-x1, y2-y1, title, "")

    return wi

class cWindow:
    # https://stackoverflow.com/a/30314197
    def __init__(self):
        self._hwnd = None
        self.shell = win32com.client.Dispatch("WScript.Shell")

    def BringToTop(self):
        win32gui.BringWindowToTop(self._hwnd)

    def SetAsForegroundWindow(self):
        self.shell.SendKeys('%')
        win32gui.SetForegroundWindow(self._hwnd)

    def Maximize(self):
        win32gui.ShowWindow(self._hwnd, win32con.SW_MAXIMIZE)

    def SetWindowSize(self, width, height):
        x0, y0, x1, y1 = win32gui.GetWindowRect(self._hwnd)
        win32gui.MoveWindow(self._hwnd, x0, y0, x0+width, y0+height, True)

    def getCoordinate(self):
        return win32gui.GetWindowRect(self._hwnd)

    def setActWin(self):
        win32gui.SetActiveWindow(self._hwnd)

    def _window_enum_callback(self, hwnd, wildcard):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        # if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
        if wildcard in str(win32gui.GetWindowText(hwnd)):
            self._hwnd = hwnd

    def find_window_wildcard(self, wildcard):
        self._hwnd = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def check_window_visibility(self):
        if self._hwnd == None:
            LogWarning(
                "Window handle was not found. check if the program exists")
            import sys
            sys.exit(0)

        while not win32gui.IsWindowVisible(self._hwnd):
            time.sleep(2)
            LogWarning(f"Wating for process {self._hwnd} to start...")

    def kill_task_manager(self):
        wildcard = 'Task Manager'
        self.find_window_wildcard(wildcard)
        if self._hwnd:
            win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.5)


def screenshot(window_title=None):
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            im = pygb.screenshot(region=(x, y, x1, y1))
            return im
        else:
            print('Window not found!')
    else:
        im = pygb.screenshot()
        return im
