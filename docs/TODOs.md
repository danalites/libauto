## TODOs
### Pending items
- [ ] Support remote task running in docker server (frontend) 
- [ ] Test WeChat OCR example

## Jan 2023
- [x] Deprecated `key.listen`
- [x] Remove record APIs (abstraction outlier)

## Dec 2022
- [x] (12/01) Handle autostart and hotkey tasks
- [x] (12/01) Code templates in task editor window

## Nov 2022
- [x] (11/30) Add example for IMAP in db ops
- [x] (11/21) Implement task editor window
- [x] (11/20) Editor window in frontend UI
- [x] (11/19) (discarded) Update hook for `hotkey` (same as `key.wait`. avoid blocking other tasks)
- [x] (11/19) Support for `data.parse` (for fuzzy search and regex)
- [x] (11/19) Fixed `key.type` entering unicode chars
- [x] (11/19) (deprecated) Support for `window.wait`
- [x] (11/19) Support for `mouse.scroll` and `cmd.while()`
- [x] (11/19) Implemented `mouse.click` and `mouse.move`
- [x] (11/19) Implemented `os.record` (auto-switching between window and global)
- [x] (11/13) Updated frontend UI (events and scheduler panel)
- [x] (11/12) Updated file read and write ops
- [x] (11/11) Fixed the CV detection dimension range issue
- [x] (11/11) Adaptively loading local tasks in user end
- [x] (11/10) (discarded) Remove $input[] and make it a global variable
- [x] (11/09) UI-icon detection service for PBD (icon mode)
- [x] (11/07) Fix the ElectroJS `wss` repeatedly initialization issue
- [x] (11/07) Add OCR server checking when starting up the service
- [x] (11/07) `TaskSch` static functions for task init and downloading
- [x] (11/02) Support `event.on`
- [x] (11/02) Update the event types for backend tasks

## Oct 2022
- [x] (10/24) (deprecated) Use priority queue to implement the crontab tasks
- [x] (10/23) Support for `$var[$val]` query
- [x] (10/23) Implement background keyboard and mouse event in `pygb`
- [x] (10/22) Add `pybind11` and `libuiohook` for IO listener
- [x] (10/22) Think about learning from recorded traces
- [x] (10/20) Introduce `window.wait()` to wait 
- [x] (10/19) Let `data.read` only used for rendering data
- [x] (10/19) Deprecate `data.write`. Use `db.write` for SQL/CSV/TXT
- [x] (10/19) Use of `window.is` region for in-window mouse/keyboard events
- [x] (10/16) Deprecate `data.get`. Use `data.read({{ VAR[..] }})` instead
- [x] (10/16) Moved OCR and speechRecognition to `libauto`
- [x] (10/16) Fixed multiple window issue in `getWindowActive` on MacOS
- [x] (10/16) Support CSV mode for `data.write()`
- [x] (10/16) Blocking mode for `task.polling`
- [x] (10/14) Deprecate `accounts` ops
- [x] (10/14) Support nested `dict[][]` in `evalExpr`
- [x] (10/14) (discarded) Support for current window annotation
- [x] (10/14) Think about cross-user information sharing (e.g., `wechat` invite)
- [x] (10/14) Think about JWT user login and web service 
- [x] (10/14) Support for `web.find.get() => ...`
- [x] (10/13) Add headless mode to `web.init`
- [x] (10/13) Implement `web.find().screenshot(FILE_NAME)`
- [x] (10/13) Think about external interface to and from 3rd part app
- [x] (10/13) Add `data.write` to save text to file
- [x] (10/13) Implement `window.ocr` and `user.input`
- [x] (10/11) Implement `key.listen` and `event.on|send`
- [x] (10/10) Support for `$env[VARS]` to get env vars
- [x] (10/10) Fix `task.configs` op interval and wait timeout
- [x] (10/09) Introduce `window.ocr` function
- [x] (10/09) Think more about use cases (desktop automation)
- [x] (10/09) Fix input value evaluation in `web.ops.type(...)`
- [x] (10/09) Support text/placeholder search in `web.find`
- [x] (10/02) Implement `key.wait` and hotkey
- [x] (10/01) Add an event hook function for tasks to inform `taskSch`
- [x] (10/01) Test for multiple connections to task scheduler `wss` server

## Sep 2022
- [x] (09/29) Add `os.shell` to run shell/ps scripts
- [x] (09/29) Deprecate `os.region`
- [x] (09/28) Deprecate `trigger` and use `hotkey` and `event.on`
- [x] (09/28) Use format from `systemd timer` https://dev.to/bowmanjd/schedule-jobs-with-systemd-timers-a-cron-alternative-15l8
- [x] (09/28) Example to record and replay mouse/keyboard actions
- [x] (09/27) Example on Nike.com account generation
- [x] (09/27) Fix local `recaptcha` solving one-click case
- [x] (09/27) Fix quote issue (string var should have quotes inside {}. )
- [x] (09/27) Support for `window.find` text OCR
- [x] (09/26) Support for sync `cmd.fn` and async `event.on`
- [x] (09/26) Support for `cmd.if` (lowered to `cmd.label` + `cmd.goto`)
- [x] (09/26) Deprecate `data.eval` and escaping comma in input commands
- [x] (09/26) GUI loading scripts and printing log
- [x] (09/26) Docker-compose [notification server](https://day.app/2018/06/bark-server-document/) + captcha + OCR
- [x] (09/25) Implement event interface (generic events, e.g., key listening)
- [x] (09/25) Change core control flow primitives (cmd.if/for)
- [x] (09/14) Support run-only-once and keep-running tasks
- [x] (09/13) Come up with a better scripts def for app bundles (`app.json`)
- [x] (09/12) Auto-download script during initialization
- [x] (09/12) Auto-task loading when GUI starts (e.g., auto-start tasks)
- [x] (09/12) Hook when a task is failed or finished
- [x] (09/11) Connect with frontend GUI key monitor
- [x] (09/11) Support for returning multiple in `data.get()`
- [x] (09/11) Improved the excel auto script
- [x] (09/10) Test global event monitor in Electron
- [x] (09/08) Added `websocket` into `aba` frontend
- [x] (09/07) Improve the logging system for async tasks
- [x] (09/07) Improve backend `libauto` programming interface

## Aug 2022
- [x] (08/19) Add `window.find(text|image)` API
- [x] (08/16) OCR text recognition on FastAPI server
- [x] (08/14) Figure out a better key monitor than `pynput`
- [x] (08/13) Allow cancelling a coroutine task
- [x] (08/12) Preliminary task scheduler GUI interface
- [x] (08/12) Move speech recognition to server
- [x] (08/06) Organizing and globing YAML scripts (search by author/names)
- [x] (08/06) Support JSON task bundle for account and app
- [x] (08/05) Update `Pyinstaller` scripts to package app
- [x] (08/05) Use Selenium 4.3.0 APIs
- [x] (08/04) Fixed python package import issue

### July 2022
- [x] (07/26) Support `cmd.countdown` to trigger callback
- [x] (07/26) A proposal for plotting figures from database table
- [x] (07/26) Better YAML file search result matching
- [x] (07/26) Support for identity generation (new and existing)
- [x] (07/26) Use `inputs[0]` to denote var in str, `$name` as variable
- [x] (07/25) Support for regex data extraction in `data` op series.
- [x] (07/25) Web op fixes (escape #, clean text from `web.get`)
- [x] (07/25) Allow `store.set` to include more keys in a table
- [x] (07/24) Example of getting amazon purchase history
- [x] (07/24) Fixed prompt for input parsing bug
- [x] (07/24) Support for web element regex matching using XPATH
- [x] (07/23) Fixed bugs in nested for loops
- [x] (07/23) Support for web ops CSS selector
- [x] (07/23) Introduce `cmd.config` to configure task executor
- [x] (07/22) OCR support `screen.find)` on active window (click to crop)
- [x] (07/22) Fixed the keyboard listener bugs.
- [x] (07/22) Introduce `cmd.func` (non-blocking callbacks)
- [x] (07/22) Game helper example: `Genshin impact`
- [x] (07/21) Fixed bugs in `cmd.goto` and `store.set/get`
- [x] (07/21) Reorganize the package file structure
- [x] (07/21) Add `cmd.print` for easy debugging 
- [x] (07/21) App example of pushing weather forecast
- [x] (07/21) Support for crontab task scheduling (countdown)
- [x] (07/20) Build a simple PoC backend using FastAPI
- [x] (07/20) Support for variable substitution inside string
- [x] (07/20) Switch to SQLite DB for local data storage
- [x] (07/19) Add XPATH extractor plugin to chrome
- [x] (07/18) Support macros to define cross-platform regions
- [x] (07/15) Define the crontab syntax: `2022-07-05T12:34:56`
- [x] (07/15) Background event listener (`key.wait`)
- [x] (07/15) Async task scheduler with hot key monitor
- [x] (07/15) Try `opencv` functions to recognize UI elements in capture
- [x] (07/15) Separate `libauto` from the GUI tool
- [x] (07/15) Real-time window capturing/monitoring with CV2
- [x] (07/15) Introduce APIs for meta-programming