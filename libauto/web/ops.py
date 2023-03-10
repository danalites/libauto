from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import seleniumwire.undetected_chromedriver as uc
# from selenium import webdriver
# from seleniumwire import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException

from libauto.core.runtime import registerOp
from libauto.utils.logger import LogInfo, LogWarning, LogError
from libauto.utils.user import getUserHome

# from .proxy import chrome_proxy_plugin
from .captcha import solve_recaptchav2_local

import os
import time
import requests
import shutil

import tempfile
import asyncio
import traceback


@registerOp
async def WEB_INIT(ctx, config: dict = {}):
    if not config:
        config = dict()

    if ctx.web_session is None:
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--disable-features=ChromeWhatsNewUI")
        chrome_options.add_argument("--window-size=660,550")

        if config.get("headless", False):
            chrome_options.add_argument("--headless")

        # ext = str(path(extensions, 'xpath-finder'))
        # LogInfo(f"XPath-Finder ext path: {ext}")
        # chrome_options.add_argument(f"--load-extension={ext}")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

        profile = config.get("profile", False)
        if profile:
            if os.path.isdir(profile):
                directory = os.path.dirname(profile)
                base = os.path.basename(profile)
                chrome_options.add_argument(f'--profile-directory={base}')

                chrome_options.add_argument(
                    f'--user-data-dir={directory}')
                LogInfo(f"Using existing profile \"{profile}\"")

            else:
                # use a standalone new profile
                directory = os.path.join(getUserHome(), "chrome")

                pdir = os.path.join(directory, profile)
                LogInfo(f"Using standalone profile \"{pdir}\"")

                if not os.path.isdir(pdir):
                    os.makedirs(pdir)

                chrome_options.add_argument(f'--profile-directory={profile}')
                chrome_options.add_argument(
                    f'--user-data-dir={directory}')

        user_agent_default = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        user_agent = config.get("user_agent", user_agent_default)
        chrome_options.add_argument(f'--user-agent={user_agent}')

        # https://daoyuan.li/configure-selenium-and-chrome-to-use-tor-proxy/
        proxy = config.get("proxy", False)
        options = {}
        if proxy:
            options = {
                'proxy': {
                    # 'https': 'https://lrhrhnil:3iu0982joqa2@185.199.229.156:7492',

                    # https://gitlab.torproject.org/woswos/CAPTCHA-Monitor/-/snippets/60
                    'http': 'socks5h://127.0.0.1:9050',
                    'https': 'socks5h://127.0.0.1:9050',
                    'connection_timeout': 10

                }
            }

        chrome_service = ChromeService(ChromeDriverManager().install())

        session = uc.Chrome(
            seleniumwire_options=options,
            options=chrome_options, service=chrome_service)
        # session.set_window_position(570, 150)

        win_size = config.get("size", None)
        if win_size:
            x, y, w, h = win_size
            session.set_window_position(x, y)
            session.set_window_size(w, h)

        # ctx.cookie = cookie
        # session.set_page_load_timeout(5)
        ctx.set_web_session(session)

    await ctx.set_next_op()


@registerOp
async def WEB_OPEN(ctx, url: str = ""):
    assert ctx.web_session is not None

    # timeout issue in chromedriver 103
    # https://bugs.chromium.org/p/chromedriver/issues/detail?id=4135&q=richa&can=2

    ctx.web_session.get(url)
    # if ctx.cookie:
    #     for c in ctx.cookie:
    #         try:
    #             ctx.web_session.add_cookie(c)
    #         except Exception as e:
    #             print(e)
    await ctx.set_next_op()


@registerOp
async def WEB_CLICK(ctx, elem):
    assert ctx.web_session is not None
    if isinstance(elem, list):
        if len(elem) > 1:
            LogWarning(f"Passed in multiple WebElements to web.click: {elem}")
        assert len(elem) > 0
        elem = elem[0]
    elem.click()
    await ctx.set_next_op()


@registerOp
async def WEB_TYPE(ctx, elem_key: str = "", val: str = ""):
    assert ctx.web_session is not None
    elem = ctx.cache[elem_key]
    elem.send_keys(val)
    await ctx.set_next_op()


def sessionHasEnded(session):
    # https://stackoverflow.com/a/52000037
    DISCONNECTED_MSG = 'Unable to evaluate script: disconnected: not connected to DevTools\n'
    if any(msg['message'] == DISCONNECTED_MSG for msg in session.get_log('driver')):
        print('Browser window closed by user')
        return True
    return False


@registerOp
async def WEB_WAIT(ctx, type: str = "", val: str = ""):
    if type == "link":
        while True:
            await asyncio.sleep(3)
            if ctx.web_session == val or sessionHasEnded(ctx.web_session):
                break

    elif type == "xpath":
        WebDriverWait(ctx.web_session, 10).until(
            EC.presence_of_element_located((By.XPATH, val)))

    else:
        while True:
            await asyncio.sleep(3)
            if sessionHasEnded(ctx.web_session):
                break

    await ctx.set_next_op()
    return


@registerOp
async def WEB_GET(ctx, target: str = "", key: str = "", ret: str = ""):
    if target == "cookie":
        all_cookies = ctx.web_session.get_cookies()

        def condition(c, target_domain):
            if target_domain in c.get("domain"):
                if not c.get("expiry"):
                    return True
                if c.get("expiry") < time.time():
                    return True
            return False

        cookies = [c for c in all_cookies if condition(c, obj)]
        ctx.cache[ret] = cookies

    elif target == "link":
        val = ctx.web_session.current_url
        ctx.cache[ret] = val

    else:
        # obj might be returned from web.find as a list
        if isinstance(target, list):
            target = target[0]

        val = target.get_attribute(key)
        if key == "textContent":
            val = val.strip().strip("\n").strip()
        ctx.cache[ret] = val

    await ctx.set_next_op()


@registerOp
async def WEB_HTTP(ctx, type: str = "", link: str = "", params: str = "", ret: str = ""):
    if type == "GET":
        headers = {
            "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }

        res = requests.get(url=link, headers=headers)
        val = None

        expected_type = params.get("type", "json")
        if expected_type == "json":
            try:
                val = res.json()
            except Exception as err:
                val = res.text
                LogWarning(err)
        
        elif expected_type == "wav":
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(res.content)
                val = f.name

        ctx.cache[ret] = val

    elif type == "DOWNLOAD":
        r = requests.get(link, stream=True)
        if r.status_code == 200:
            r.raw.decode_content = True

            with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
                shutil.copyfileobj(r.raw, f)
                ctx.cache[ret] = f.name
        else:
            LogWarning(f"Failed to download {link}")

    await ctx.set_next_op()


@registerOp
async def WEB_UTILS(ctx, task: str = ""):
    assert ctx.web_session is not None

    if task == "solve-recaptcha-v2-local":
        await solve_recaptchav2_local(ctx.web_session)

    await ctx.set_next_op()


def webParseRet(ret):
    if ret.startswith(".click"):
        return {"type": "CLICK"}

    elif ret.startswith(".type"):
        val = ret.rstrip(")").split("(", 1)[-1].strip("\"")
        LogWarning(f"WEB_OPS type: \"{val}\"")
        return {"type": "TYPE", "val": val}

    elif ret.startswith(".select"):
        val = ret.rstrip(")").split("(", 1)[-1]
        return {"type": "SELECT", "val": val}

    elif ".get" in ret:
        ret, key = ret.split("|")
        attr = key.rstrip(")").split("(", 1)[-1]
        return {"type": "GET", "val": attr, "ret": ret}

    else:
        return {"type": "NONE"}


def webElemAction(elem, action):
    if action["type"] == "CLICK":
        elem.click()

    elif action["type"] == "TYPE":
        elem.clear()
        elem.send_keys(action["val"])

    elif action["type"] == "SELECT":
        Select(elem).select_by_visible_text(action["val"])

    elif action["type"] == "GET":
        return {
            "key": action["ret"],
            "val": elem.get_attribute(action["val"])
        }

    elif action["type"] == "NONE":
        return None


@registerOp
async def WEB_FIND(ctx, selector: str = "", text: str = "", ret: str = ""):
    if ctx.web_session is None:
        LogError("WEB_OPS. No web session found")

    action = webParseRet(ret)
    if text:
        # Placeholder text selector
        selector = f"//input[@placeholder='{text}']"
        elem_type = By.XPATH

    elif selector.lstrip("(").startswith("//"):
        elem_type = By.XPATH

    else:
        elem_type = By.CSS_SELECTOR

    try:
        elems = ctx.web_session.find_elements(elem_type, selector)
        if len(elems) == 0:
            raise NoSuchElementException(f"Selector \"{selector}\" not found")
        elem = elems[0]
        if len(elems) > 1:
            LogWarning(f"Found multiple elements {selector}")

        val = webElemAction(elem, action)
        if val is None:
            LogWarning(f"WEB_OPS: No action specified. Selector: {selector}")
            ctx.cache[ret] = elems
        else:
            LogWarning(f"WEB_OPS: AttrGet ${val['key']} <= {val['val']}")
            ctx.cache[val["key"]] = val["val"]

    except NoSuchElementException as e:
        t = ctx.op_wait_timeout
        LogWarning(f"WEB_FIND: {selector} not found. Wait for {t} s")
        # wait = WebDriverWait(ctx.web_session, t)
        # elems = wait.until(
        #     EC.element_to_be_clickable((elem_type, selector)))

        await asyncio.sleep(t)
        elems = ctx.web_session.find_elements(elem_type, selector)

        if len(elems) == 0:
            LogWarning(f"Selector \"{selector}\" not found")
            ctx.cache[ret] = None

        else:
            elem = elems[0]
            if len(elems) > 1:
                LogWarning(f"Found multiple elements {selector}")

            val = webElemAction(elem, action)
            if val is None:
                ctx.cache[ret] = elems
            else:
                ctx.cache[val["key"]] = val["val"]

    except InvalidSelectorException as err:
        LogWarning(f"invalid selector {selector}")

    except Exception as err:
        LogWarning(f"{selector} - Exception. {err}")
        traceback.print_exc()
        ctx.cache[ret] = None

    await ctx.set_next_op()
