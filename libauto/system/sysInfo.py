import platform
import sys
import os

# https://apple.stackexchange.com/a/89034
macCodeNames = {
    "10.0":	"Cheetah",
    "10.1":	"Puma",
    "10.2":	"Jaguar",
    "10.3":	"Panther",
    "10.4":	"Tiger",
    "10.5":	"Leopard",
    "10.6":	"Snow Leopard",
    "10.7":	"Lion",
    "10.8":	"Mountain Lion",
    "10.9":	"Mavericks",
    "10.10": "Yosemite",
    "10.11": "El Capitan",
    "10.12": "Sierra",
    "10.13": "High Sierra",
    "10.14": "Mojave",
    "10.15": "Catalina",
    "11":	"Big Sur",
    "12":	"Monterey",
    "13":	"Ventura"
}


class OsEnv:
    def __init__(self, os_type, ver=None, build_num=None, code=None):
        self.os_type = os_type
        self.os_ver = ver
        self.os_build = build_num
        self.code_name = code


def getEnvInfo():
    if sys.platform == "darwin":
        build = os.popen("sw_vers -buildVersion").read().strip()
        ver_num = float(os.popen("sw_vers -productVersion").read().strip())
        ver_key = int(ver_num) if ver_num >= 11 else ver_num
        codeName = macCodeNames[str(ver_key)]
        return OsEnv("darwin", ver_num, build, codeName)

    elif sys.platform == "win32":
        return OsEnv("win32", platform.version())

