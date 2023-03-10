class Event:
    O_EVENT_TASK_STATUS = "O_EVENT_TASK_STATUS"

    # Event actions (e.g., register, invoke or remove events)
    O_EVENT_TASK_EVENT_REQ = "O_EVENT_TASK_EVENT_REQ"

    # IO hooks (e.g., key.wait or __KEY_PRESSED events)
    O_EVENT_HOOK_REQ = "O_EVENT_HOOK_REQ"

    # Send request to user blocking the task (user.input)
    O_EVENT_USER_INPUT = "O_EVENT_USER_INPUT"
    
    # Notify user without blocking the task (user.notify)
    O_EVENT_USER_NOTIFY = "O_EVENT_USER_NOTIFY"

    # Window request (e.g., window annotation)
    O_EVENT_WINDOW_REQ = "O_EVENT_WINDOW_REQ"

    # Console task requests (run, cancel, or resume task)
    I_EVENT_TASK_REQ = "I_EVENT_TASK_REQ"

    @staticmethod
    def new(event_type: str, uuid: str = "", args=dict()):
        event = {"event": event_type, "uuid": uuid, "value": args}
        return event