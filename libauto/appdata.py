import re
import os
import json
import yaml
import sqlite3

from libauto.utils.logger import LogError, LogWarning, LogInfo
from libauto.utils.downloader import download
from libauto.core.event import Event
from libauto.utils.user import getUserHome


def getUserScripts():
    appdata = getUserHome("scripts")

    # Map from app name to task list
    apps = list()
    config = "tasks.json"

    # Example task 
    for parent, directories, files in os.walk(appdata):
        if config in files:
            LogWarning(f"(Appdata) Found \"{parent}/{config}\"")
            with open(os.path.join(parent, config), 'r') as f:
                manifest = json.load(f)
                app = dict()
                app["name"] = manifest["app"]
                app["icon"] = manifest["logo"]
                app["author"] = manifest["author"]
                app["path"] = parent
                app_tasks = list()

                count = 0
                for task_path in manifest["tasks"]:
                    task = dict()
                    abs_path = os.path.join(parent, task_path)

                    with open(abs_path, 'r') as f:
                        code = f.read()

                    with open(abs_path, "r", encoding="utf8") as stream:
                        try:
                            content = yaml.safe_load(stream)
                            task["key"] = count
                            task["name"] = content["task"]
                            task["dir"] = os.path.dirname(abs_path) + os.path.sep
                            task["path"] = os.path.basename(abs_path)

                            inputs = [] 
                            for k, v in content.get("inputs", {}).items():
                                inputs.append({"key": k, "value": v})
                                
                            task["inputs"] = inputs
                            task["desc"] = content.get("desc", [])
                            task["demo"] = content.get("demo", "")
                            task["content"] = code

                            # Execution options (remote, endless, autostart)
                            task["options"] = []

                            # start-time, op-interval
                            if "configs" in content:
                                for k, v in content["configs"].items():
                                    # E.g., start-time to startTime
                                    index = k.find("-")
                                    if index > -1:
                                        chars = list(k.replace("-", ""))
                                        chars[index] = chars[index].upper()
                                        k = "".join(chars)
                                    if k == "options":
                                        for opt in v:
                                            if opt in ["remote", "endless", "autostart"]:
                                                task["options"].append(opt)
                                    else:            
                                        task[k] = v

                            app_tasks.append(task)
                            count += 1

                        except yaml.YAMLError as exc:
                            LogError(exc)

                app["tasks"] = app_tasks
                apps.append(app)
    
    args = {"type": "loadTasks", "tasks": apps}
    return Event.new(Event.O_EVENT_TASK_STATUS, uuid="NULL", args=args)


def initUserData(repo_urls=list()):
    new_user = False
    appdata = getUserHome()

    if not os.path.exists(appdata):
        new_user = True
        os.makedirs(appdata)

    sub_dirs = list()
    sub_dirs.append(os.path.join(appdata, "chrome"))
    sub_dirs.append(os.path.join(appdata, "logs"))
    sub_dirs.append(os.path.join(appdata, "scripts"))

    for sub_dir in sub_dirs:
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
            new_user = True

    default_db = os.path.join(appdata, "aba.db")
    if not os.path.exists(default_db):
        con = sqlite3.connect(default_db)
        cur = con.cursor()
        cur.execute(
            "create table default_table (key TEXT PRIMARY KEY, val TEXT)")
        cur.close()
        con.close()

    if new_user:
        for url in repo_urls:
            downloadToUserApp(url)

    return getUserScripts()


def downloadToUserApp(url):
    # https://github.com/danalites/apps/tree/master/games/genshin
    pattern = r"https:\/\/github\.com\/(\w+)\/.*\/(\w+)"
    matches = re.match(pattern, url)

    if not matches:
        raise RuntimeError(f"Invalid github link given: {url}")

    author, app = matches[1], matches[2]
    paths = [getUserHome(), "scripts", author, app]
    script_path = os.path.join(*paths)

    if not os.path.exists(script_path):
        LogInfo(f"downloader: retrieving scripts from {url} to {script_path}")
        os.makedirs(script_path, exist_ok=True)
        download(url, output_dir=script_path, folder_name=app)

    else:
        LogInfo(f"downloader: scripts exist in {script_path}")


if __name__ == "__main__":
    repo_url = "https://github.com/AbaTech/apps/tree/main/excel"
    downloadToUserApp(repo_url)
