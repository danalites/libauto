import iohook
import time
from concurrent.futures import ThreadPoolExecutor

g_counter = 0

def foo(i):
  global g_counter
  print(i)
  g_counter = g_counter + 1

s = iohook.System()
s.registerCallback(foo)

# s.start()
print("Started...")

# Stuck here
s.start_event_loop()
s.start()

while g_counter < 10:
  print("waiting...")
  time.sleep(3)

s.stop()
