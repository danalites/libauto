### I_EVENT
Each event will need an UUID to (1) identify the event initiated the request in ElectronJS, and (2) return input to background task mailbox
  
- [x] User input (select window region, ask for user selection), or key stroke for task registered `key.wait|listen` 

```json
{   "event": "I_EVENT_USER_INPUT",
    "value": { "type": "mouseUp", "location": [0, 100, 250, 250] }}
```

- [x] User request to start or cancel a task. TBA: or a specific op in a task (break point or step in debugging)

```json
{   "event": "I_EVENT_TASK_REQ",
    "value": { "type": "RUN", "location": "", "configs": {}}}
```

