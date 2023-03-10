import asyncio
import requests

# import iohook
from collections import deque

from libauto.utils.logger import LogInfo, LogWarning, LogCritical
from libauto.core.context import executeOps
from libauto.core.task import Task, TaskStatus
from libauto.core.eventProxy import EventProxy
from libauto.core.event import Event
from libauto.appdata import initUserData


def exception_handler(loop, context):
    LogWarning(f"(TaskSch) Exception:  {context}")


class TaskSch:
    def __init__(self):
        self.task_queue = deque([], 10)
        self.task_queue_ready = deque([], 10)

        # task status tracking
        self.tasks_table = dict()
        self.running = False

        self.event_loop = asyncio.new_event_loop()
        self.event_loop.set_exception_handler(exception_handler)

        # EventProxy is a centralized store to publish/subscribe events
        # self.iohook = iohook.System()
        # self.iohook.registerCallback(foo)

        self.service = dict()
        self.event_proxy = EventProxy(self.tasks_table)
        self.event_proxy.set_callback(self.event_proxy_callback)

    def init(self):
        repo_urls = [
            "https://github.com/AbaTech/apps/tree/main/excel-helpers"
        ]
        # Check if OCR and speech recognition is running
        # ocr_server = "http://localhost:8866"
        # try:
        #     resp = requests.get(ocr_server)
        #     if resp.status_code != 200:
        #         raise Exception
        #     self.service["OCR"] = True
        # except:
        #     LogCritical(
        #         f"OCR server is not running. window.find/ocr won't work.")
        return initUserData(repo_urls)

    def cancel_task(self, uuid):
        if uuid in self.tasks_table:
            coro = self.tasks_table[uuid]["coro"]
            task = self.tasks_table[uuid]["task"]
            if coro.cancelled() or coro.done():
                LogWarning(f"task {task} finished/failed before cancelling.")
            else:
                coro.cancel()
                LogWarning(f"{task} is stopped.")
        else:
            LogWarning(f"task({uuid}) finished before cancel().")

    def submit(self, tasks: list[Task]):
        for task in tasks:
            self.tasks_table[task.uuid] = {
                "task": task,
                "coro": None,
                "status": TaskStatus.INIT,
            }
            # Multiple coroutines in sub-group
            num = task.configs.get("task-count", 1)
            for index in range(num):
                task.index = index
                self.task_queue_ready.append(task)
        LogInfo(f"Submitting tasks to queue {tasks}")

    def event_proxy_callback(self, target, task):
        if target == "RUN":
            self.tasks_table[task.uuid] = {
                "task": task,
                "coro": None,
                "status": TaskStatus.INIT,
            }
            self.task_queue_ready.append(task)
        elif target == "CANCEL":
            self.cancel_task(task)

    def stop(self):
        self.running = False

    def task_done_callback(self, future: asyncio.Future):
        exception = future.exception()
        uuid = future.uuid

        task = self.tasks_table[uuid]["task"]

        status = {"type": "taskFinish", "name": task.name, "code": int(
            TaskStatus.FINISHED), "message": f"Task({task.name}, {uuid}) finished."}
        if exception:
            LogWarning(f"(Exception) ({task.name}, {uuid}). " + str(exception))
            status["type"] = "taskError"
            status["code"] = int(TaskStatus.FAILED)
            status["message"] = str(exception)
        else:
            LogWarning(f"(TaskSch) Task({task.name}, {uuid}) finished.")

        event = Event.new(Event.O_EVENT_TASK_STATUS, uuid=uuid, args=status)
        self.event_proxy.o_queue.append(event)

    async def recv_event_from_task(self, event):
        return await self.event_proxy.register_event(event)

    async def start(self):
        self.running = True
        while self.running:
            await asyncio.sleep(0.5)

            if self.task_queue_ready:
                task = self.task_queue_ready.pop()
                LogInfo(f"TaskSch: Execute new task \"{task.name}\"")

                # taskSch recv/send events from/to tasks
                coro = asyncio.create_task(executeOps(
                    task, event_channel=self.recv_event_from_task))

                # add callback for debug handling
                # https://stackoverflow.com/a/35789404
                coro.add_done_callback(self.task_done_callback)
                coro.uuid = task.uuid
                self.tasks_table[task.uuid]["coro"] = coro
