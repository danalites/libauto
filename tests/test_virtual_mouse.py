import Quartz
import objc

# https://stackoverflow.com/questions/42657655/how-to-send-mouse-click-event-to-a-window-in-mac-osx


pid = 549  # get/input a real pid from somewhere for the target app.

point = Quartz.CGPoint()
point.x = 62  # get a target x from somewhere
point.y = 22  # likewise, your target y from somewhere

# Quartz.kCGEventMouseMoved
# left_mouse_down_event = Quartz.CGEventCreateMouseEvent(objc.NULL, Quartz.kCGEventLeftMouseDown, point, Quartz.kCGMouseButtonLeft)
# left_mouse_up_event = Quartz.CGEventCreateMouseEvent(objc.NULL, Quartz.kCGEventLeftMouseUp, point, Quartz.kCGMouseButtonLeft)

keyboard_event = Quartz.CGEventCreateKeyboardEvent(objc.NULL, 3, True)
keyboard_event1 = Quartz.CGEventCreateKeyboardEvent(objc.NULL, 3, True) #F

# Quartz.CGEventPostToPid(pid, left_mouse_down_event)
# Quartz.CGEventPostToPid(pid, left_mouse_up_event)
Quartz.CGEventPostToPid(pid, keyboard_event)

# https://www.jianshu.com/p/59c1a3df4aaa
# https://www.jianshu.com/p/b5d7ce626003
print(Quartz.CGEventGetFlags(keyboard_event1))
Quartz.CGEventSetFlags(keyboard_event1, Quartz.kCGEventFlagMaskCommand)
Quartz.CGEventPostToPid(pid, keyboard_event1)