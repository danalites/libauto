import os
import time
import yaml
import uuid as uuidlib
from enum import IntEnum

from libauto.utils.user import getUserHome
from libauto.utils.logger import LogError, LogWarning


class TaskStatus(IntEnum):
    # Task not queued
    INIT = 0
    # Task queued waiting for hotkey to start
    PENDING = 1
    # Paused (waiting for input/key stroke)
    PAUSED = 2
    # Still running
    ACTIVE = 3
    # Task exited with exception
    FAILED = 4
    # Task exited normally
    FINISHED = 5


class Task:
    def __init__(self, name, ops, inputs=dict(),
                 configs=dict(), source=None, cache=None, uuid=None):

        self.name = name
        self.index = 0
        self.uuid = uuid if uuid else str(uuidlib.uuid4())
        self.init_time = time.time()
        self.ops = ops

        self.inputs = inputs
        self.cache = cache
        self.configs = configs

        # YAML source file
        self.source = source

    def __hash__(self):
        return hash(str(self.uuid))

    def __repr__(self):
        return f"Task({self.name}, {self.uuid})"

    def has(self, prop):
        return self.configs.get()


def genTaskFromYAML(content, source=None, uuid=None):
    name = content.get("task").strip().replace(" ", "_")
    ops = content.get("actions")

    kwargs = {
        "inputs": dict(),
        "configs": dict(),
        "uuid": uuid,
    }

    for k, v in kwargs.items():
        if k in content:
            val = content[k]
            kwargs[k] = val

    if source:
        kwargs["source"] = os.path.abspath(source)

    return Task(name, ops, **kwargs)


def loadTasks(sources):
    tasks = list()
    for s in sources:
        tasks.append(loadTask(s))
    return tasks


def loadTask(source, uuid=None):
    if not os.path.exists(source):
        appdata = getUserHome("scripts")
        LogWarning(f"(loading task) searching {source} in {appdata}")

    with open(source, "r", encoding="utf8") as stream:
        try:
            content = yaml.safe_load(stream)
            return genTaskFromYAML(content, source, uuid)
        except yaml.YAMLError as exc:
            LogError(exc)
