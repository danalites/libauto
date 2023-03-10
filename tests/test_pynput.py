from pynput import keyboard
import time

# https://github.com/moses-palmer/pynput/issues/20
COMBINATIONS = [
    frozenset({keyboard.Key.shift, keyboard.KeyCode(char='a')}),
    frozenset({keyboard.Key.shift, keyboard.KeyCode(char='A')}),
    frozenset({keyboard.Key.cmd, keyboard.Key.ctrl})
]

# The currently active modifiers
current = set()


def execute():
    print("Do Something")


def on_press(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.add(key)
        print("PPP", current)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            execute()


def on_release(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        print(current, key)
        current.remove(key)


listener_keyboard = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

listener_keyboard.start()
time.sleep(15)
