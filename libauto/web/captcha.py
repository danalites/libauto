import re
import sys
import asyncio

import os
import json
import base64
import urllib.request
import requests

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from libauto.utils.user import getUserHome
from libauto.utils.logger import LogInfo, LogWarning


async def delay():
    return await asyncio.sleep(3.5)


async def solve_recaptchav2_local(driver):
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    recaptcha_control_frame = None
    recaptcha_challenge_frame = None
    for index, frame in enumerate(frames):
        if re.search('reCAPTCHA', frame.get_attribute("title")):
            recaptcha_control_frame = frame

        if re.search('recaptcha challenge', frame.get_attribute("title")):
            recaptcha_challenge_frame = frame

    if not (recaptcha_control_frame and recaptcha_challenge_frame):
        LogWarning("(ERR) Unable to find recaptcha. Abort solver.")
        sys.exit()

    # switch to recaptcha frame
    await delay()
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(recaptcha_control_frame)

    # click on checkbox to activate recaptcha
    driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()

    # recaptcha one-click
    await delay()
    driver.switch_to.default_content()
    try:
        if driver.find_element(By.CLASS_NAME, "recaptcha-success"):
            LogWarning("(recpatcha) one-click success. returning")
            return
    except NoSuchElementException:
        pass

    # switch to recaptcha audio control frame
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(recaptcha_challenge_frame)

    # click on audio challenge
    driver.find_element(By.ID, "recaptcha-audio-button").click()

    # switch to recaptcha audio challenge frame
    driver.switch_to.default_content()
    frames = driver.find_elements(By.TAG_NAME, "iframe")
    driver.switch_to.frame(recaptcha_challenge_frame)

    # get the mp3 audio file
    await delay()
    src = driver.find_element(By.ID, "audio-source").get_attribute("src")
    LogInfo(f"(WEB_UTILS) MP3 audio src: {src}")

    apppath = getUserHome()
    path_to_mp3 = os.path.join(apppath, "sample.mp3")

    # download the mp3 audio file from the source
    urllib.request.urlretrieve(src, path_to_mp3)

    # start voice recognition
    with open(path_to_mp3, 'rb') as f:
        base64_bytes = base64.b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
    data = {'audio': base64_string}
    value = requests.post("http://localhost:8865/speech", json=data).text
    key = json.loads(value)["result"]
    LogInfo(f"Google RecaptchaV2 Passcode: {key}")

    await delay()
    driver.find_element(By.ID, "audio-response").send_keys(key.lower())
    driver.find_element(By.ID, "audio-response").send_keys(Keys.ENTER)
    await delay()
    driver.switch_to.default_content()
    await delay()

    try:
        driver.find_element(By.ID, "recaptcha-demo-submit").click()
    except Exception as e:
        LogWarning("Unable to click submit button. Abort solver.")
