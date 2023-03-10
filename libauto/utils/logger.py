import sys
import pkgutil
import logging
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def promptForInput(message):
    output = str()
    machine = sys.platform
    if machine == "darwin":
        # https://stackoverflow.com/a/58941536
        content = pkgutil.get_data(
            str(__name__), "assets/osx/prompt-for-text.applescript").decode("utf-8")

        c = content.replace("{argv0}", message)

        cmd = ["osascript"]
        for l in c.split("\n"):
            cmd.append("-e")
            cmd.append(l.strip())

        out = subprocess.run(cmd, capture_output=True)
        output = out.stdout.decode("utf8")

        if not "text returned" in output:
            LogWarning(f"applescript error, {out.stderr}")
        output = output.split("text returned:")[-1].rstrip("\n")
    
    elif machine == "win32":
        pass

    return output


def LogInfo(msg):
    print(f"{bcolors.OKGREEN}[INFO]    {msg}{bcolors.ENDC}")

def LogWarning(msg):
    print(f"{bcolors.WARNING}[WARNING] {msg}{bcolors.ENDC}")

def LogCritical(msg):
    print(f"{bcolors.OKCYAN}[CRITICAL]{msg}{bcolors.ENDC}")

def LogError(msg):
    print(f"{bcolors.FAIL}[ERROR]    {msg}{bcolors.ENDC}")
    sys.exit()
