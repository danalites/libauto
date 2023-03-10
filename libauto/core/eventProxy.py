import time
import asyncio

from libauto.utils.logger import LogCritical, LogError, LogWarning
from libauto.core.task import Task, loadTask
from libauto.core.event import Event

class EventProxy:
    def __init__(self, tasks_table):
        # Map of task uuid to coro; eventName to taskOps
        self.event_table = dict()
        self.tasks_table = tasks_table

        # Outwards Queue to issue requests
        self.o_queue = list()
        self.mail_box = dict()

    async def register_event(self, event):
        LogWarning(f"(EventProxy) register event: {event}")
        self.o_queue.append(event)
        data = event["value"]

        uuid = event.get("uuid")
        task_name = event.get("taskName")
        event_type = event.get("event")

        # Event registration (mount to event bus)
        if event_type == Event.O_EVENT_TASK_EVENT_REQ:
            sub_type = data["type"]
            event_name = data["eventName"]

            if sub_type == "eventRegister":
                entry = {"uuid": uuid, "taskOps": data.get(
                    "taskOps"), "argsName": data.get("argsName")}
                self.event_table[event_name] = entry
            
            elif sub_type == "eventInvoke":
                if event_name in self.event_table:
                    entry = self.event_table[event_name]
                    args = { entry["argsName"]: data.get("args") }
                    task = Task(event_name, entry["taskOps"], cache=args)
                    self.callback("RUN", task)
                else:
                    LogCritical(f"(EventProxy) event {event_name} not registered")

        elif event_type in [Event.O_EVENT_HOOK_REQ, Event.O_EVENT_USER_INPUT]:
            # blocking for keyWait or userInput
            return await self.polling(task_name, uuid)

        elif event_type == Event.O_EVENT_USER_NOTIFY or event_type == Event.O_EVENT_WINDOW_REQ:
            pass

        else:
            LogError(
                f"(EventProxy) register_event: unknown event type {event}")

    async def polling(self, task_name, uuid, blocking=False):
        LogWarning(f"(EventProxy) {task_name}({uuid}) waiting...")
        while True:
            if uuid in self.mail_box:
                response = self.mail_box[uuid]
                del self.mail_box[uuid]
                LogWarning(
                    f"(EventProxy) resp for {task_name}({uuid}): {response}")
                return response
            if blocking:
                time.sleep(0.3)
            else:
                await asyncio.sleep(0.3)

    def set_callback(self, callback):
        self.callback = callback

    def resolve(self, event):
        LogWarning(f"(EventProxy) i_queue \"{event}\"")
        event_type, uuid = event["event"], event["uuid"]
        data = event["value"]

        # User request to run/cancel a task
        if event_type == Event.I_EVENT_TASK_REQ:
            if data["type"] == "eventTask":
                event_name = data["eventName"]

                if event_name in self.event_table:
                    entry = self.event_table[event_name]
                    args = { entry["argsName"]: data["args"] }
                    task = Task(event_name, entry["taskOps"], cache=args)
                    self.callback("RUN", task)
                else:
                    LogCritical(f"(EventProxy) event {event_name} not registered")

            elif data["type"] == "cancelTask":
                self.callback("CANCEL", uuid)
            
            elif data["type"] == "resumeTask":
                self.mail_box[uuid] = data

            else:
                # Example format from user end
                #   name: "copy-sheet",
                #   appPath: "C:\\Users\\Administrator\\AppData\\",
                #   taskPath: "Subdir\\Local.yaml",
                #   startTime: "Mon,Wed *-1..11-* 23:00 UTC",
                #   options: ["remote"],
                #   content: ...
                location = data["absTaskPath"]
                if "content" in data:
                    with open(location, "w") as f:
                        f.write(data["content"])

                task = loadTask(location, uuid)
                if "inputs" in data:
                    inputs = data["inputs"]
                    inputs_dict = dict()
                    for i in inputs:
                        inputs_dict[i["key"]] = i["value"]
                    task.inputs = inputs_dict
                self.callback("RUN", task)

        else:
            LogError(f"(EventProxy) resolve: unknown event type {event}")
