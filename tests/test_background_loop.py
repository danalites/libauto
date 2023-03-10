import asyncio
import time
import threading


class Sensor:
    def __init__(self, start=0):
        self.num = start

    async def update(self):
        print(f"Starting Updates{self.num}")
        while True:
            self.num += 1
            print(self.num)
            await asyncio.sleep(1)


if __name__ == "__main__":
    # https://stackoverflow.com/a/63860274

    print("Main")
    sensor1 = Sensor()
    sensor2 = Sensor()

    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever).start()

    future1 = asyncio.run_coroutine_threadsafe(sensor1.update(), loop)
    future2 = asyncio.run_coroutine_threadsafe(sensor2.update(), loop)

    print("We are back")
    print(f"current value: {sensor1.num}")
    time.sleep(4)

    print(f"current value: {sensor1.num}")
    loop.call_soon_threadsafe(loop.stop)
