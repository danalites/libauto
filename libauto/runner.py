import sys
import asyncio
import traceback
import threading

from libauto.core.context import executeOps
from libauto.core.task import loadTask
from libauto.core.taskSch import TaskSch
from libauto.utils.logger import LogError, LogInfo


def executeTaskYAML(ops_in_yaml):
    task = loadTask(ops_in_yaml)
    LogInfo(f"taskRunner: task {task} loaded.")
    try:
        asyncio.run(executeOps(task))
    except Exception as e:
        traceback.print_exc()
        LogError("Exiting due to exception {}: {}".format(type(e).__name__, e))


async def executeTasksWithSch(tasks, time_out=20):
    ts = TaskSch(new_event_loop=False)
    # run task scheduler in main thread
    # https://stackoverflow.com/a/70758990
    async def timer():
        await asyncio.sleep(time_out)
        ts.stop()

    workers = [
        asyncio.create_task(ts.start()),
        # asyncio.create_task(ts.crontab_tasks_countdowns())
    ]

    ts.submit(tasks)
    if time_out:
        workers.append(asyncio.create_task(timer()))
        await asyncio.wait(workers, return_when=asyncio.FIRST_COMPLETED)


def createTaskSchCoroutines():
    # run task scheduler in the background
    ts = TaskSch()
    threading.Thread(target=ts.event_loop.run_forever).start()
    asyncio.run_coroutine_threadsafe(ts.start(), ts.event_loop),
    # asyncio.run_coroutine_threadsafe(
    #     ts.crontab_tasks_countdowns(), ts.event_loop)
    return ts


if __name__ == "__main__":
    yaml_source = sys.argv[1]
    ts = createTaskSchCoroutines()
    ts.submit(loadTask(yaml_source))
