import os
import io

import json
import time
import base64
import asyncio
import requests

import pygb
from difflib import SequenceMatcher

from libauto.utils.logger import LogWarning
from libauto.core.runtime import registerOp
from libauto.core.event import Event

from libauto.system.window import getActiveWindow, getOpenWindow


def cv2_to_base64(image):
    with io.BytesIO() as output:
        image.save(output, format="PNG")
        contents = output.getvalue()
    return base64.b64encode(contents).decode('utf8')


def screenshotActive(region: list = []):
    wi = getActiveWindow()
    origin = wi.lt
    width, height = wi.wh

    # if sys.platform == "darwin":
    #     if subprocess.call("system_profiler SPDisplaysDataType | grep -i 'retina'", shell=True) == 0:
    #         LogWarning(
    #             f"retina screen used. try to scale up the bbox size {bbox}")
    #         bbox = tuple([_ * 2 for _ in bbox])
    if region:
        # absolute region (relative to window)
        if any(v > 1 for v in region):
            LogWarning(
                f"(getActiveWindow) coordinates {region}")
            lt = (origin[0] + region[0], origin[1] + region[1])
            wh = (region[2], region[3])
            bbox = (*lt, *wh)

        # relative region in percentage
        # E.x. [0.1, 0.3, 0.8, 0.9] => X(10%-30%), Y(80%-90%)
        else:
            lt = (origin[0] + region[0] * width,
                  origin[1] + region[2] * height)
            wh = ((region[1]-region[0])*width, (region[3]-region[2])*height)
            bbox = (*lt, *wh)
            LogWarning(
                f"(getActiveWindow) use relative coordinates {region} => {bbox}")

    im = pygb.screenshot(region=bbox)
    return origin, im


@registerOp
async def WINDOW_OCR(ctx, region=list(), ret: str = ""):
    LogWarning(f"WINDOW_OCR: doing OCR over relative region: {region}")
    origin, roi = screenshotActive(region)
    roi.save("ocr.png")

    headers = {"Content-type": "application/json"}
    data = {'images': [cv2_to_base64(roi)]}
    r = requests.post(
        url="http://localhost:8866/predict/ocr_system", headers=headers, data=json.dumps(data))
    res = r.json()["results"][0]

    # Return a flattened text without location information
    text = str()
    for line in res:
        text += line["text"] + " "

    ctx.cache[ret] = text
    await ctx.set_next_op()


@registerOp
async def WINDOW_WAIT(ctx, target: str = "", config=dict()):
    region = config.get("region", None)
    interval = config.get("interval", 1)
    similarity = config.get("similarity", 0.8)

    if target == "*":
        ctx.log_warning(f"(WINDOW_FIND) waiting for changes in {region}")
        changed = False
        im = pygb.screenshot(region=region)
        while not changed:
            await asyncio.sleep(interval)
            changed = pygb.locate(im, new_im, similarity)

    else:
        found = False
        config = dict()
        if region:
            config["region"] = region
        while not found:
            location = await WINDOW_FIND(ctx, target, config)
            if location:
                found = True
            else:
                await asyncio.sleep(interval)

    await ctx.set_next_op()


@registerOp
async def USER_INPUT(ctx, params: dict = {}, ret: str = ""):
    event = Event.new(Event.O_EVENT_USER_INPUT, args=params)
    result = await ctx.send_event_to_ts(event)
    ctx.log_warning(f"USER_INPUT: resolved \"{result}\". Continue...")

    ctx.cache[ret] = result["selected"]
    await ctx.set_next_op()


@registerOp
async def WINDOW_FIND(ctx, target: str = "", config=dict(), ret: str = ""):
    location = None
    imgs = ("png", "jpg", "jpeg")
    base = os.path.dirname(ctx.yaml_src)
    cache = os.path.join(base, ".cache")
    if not os.path.exists(cache):
        os.makedirs(cache)

    # The region to find text/image of interest
    region = config.get("region", [0, 0, 1, 1])

    if target.endswith(imgs):
        # 1. Locate image on window/screen
        if not os.path.exists(target):
            location = os.path.join(base, f"{target}.png")
            if not os.path.exists(location):
                raise RuntimeError(f" (WIN_FIND) not found \"{location}\"")
        location = pygb.locateOnScreen(img, confidence=.7)

    elif target == "*":
        # 2. Auto detect graphic blocks on window/screen
        origin, roi = screenshotActive(region)
        headers = {"Content-type": "application/json"}
        data = {'images': [cv2_to_base64(roi)]}
        r = requests.post(
            url="http://localhost:8866/predict/ocr_system", headers=headers, data=json.dumps(data))
        res = r.json()["results"]

    else:
        # 3. Locate text on the window/screen
        cached = False
        img = os.path.join(cache, f"{target}.png")
        if os.path.exists(img):
            LogWarning(f"Found cache: {img}. Skip OCR")
            cached = True
            location = pygb.locateOnScreen(img, confidence=.7)

        if not cached:
            origin, roi = screenshotActive(region)
            headers = {"Content-type": "application/json"}
            data = {'images': [cv2_to_base64(roi)]}
            r = requests.post(
                url="http://localhost:8866/predict/ocr_system", headers=headers, data=json.dumps(data))
            res = r.json()["results"]

            for r in res[0]:
                if SequenceMatcher(None, r["text"], target).ratio() > 0.8:
                    coordinates = r["text_region"]
                    # Include offset of original image
                    pos = (*coordinates[0], *coordinates[2])
                    location = (pos[0]+origin[0], pos[1]+origin[1],
                                pos[2]+origin[0], pos[3]+origin[1])
                    break

    ctx.cache[ret] = location
    await ctx.set_next_op()


@registerOp
async def WINDOW_IS_ACTIVE(ctx, name: str = "", ret: str = ""):
    wi = getActiveWindow()
    LogWarning(f"(WINDOW_IS_ACTIVE): {wi}")
    ret_val = wi.__dict__
    if name:
        if name not in wi.owner:
            ret_val = False

    ctx.cache[ret] = ret_val
    await ctx.set_next_op()


@registerOp
async def WINDOW_ENTER(ctx, win_name: str = "", options: dict = {}):
    wi = getOpenWindow(win_name)
    LogWarning(f"(WINDOW_IS): {wi}")

    timeout = options.get("timeout", 0)
    if wi:
        ctx.window = wi
    else:
        if timeout > 0:
            start = time.time()
            while time.time() - start < timeout:
                wi = getOpenWindow(win_name)
                if wi:
                    ctx.window = wi
                    break
                await asyncio.sleep(0.5)
        else:
            raise RuntimeError(f"Window \"{win_name}\" is not open")
    await ctx.set_next_op()


@registerOp
async def WINDOW_EXIT(ctx):
    ctx.window = None
    await ctx.set_next_op()


@registerOp
async def WINDOW_ANNOTATE(ctx, config: dict = {}):
    origin = (0, 0)
    if ctx.window is not None:
        ctx.log_warning(f"WIN_ANNOTATE: on {ctx.window}")
        origin = ctx.window.lt

    event = Event.new(Event.O_EVENT_WINDOW_REQ, args={
        'type': 'windowAnnotate', 'origin': origin, **config})

    await ctx.send_event_to_ts(event)
    await ctx.set_next_op(time=0.01)
