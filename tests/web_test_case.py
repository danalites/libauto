from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver.v2 as uc
import time


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-features=ChromeWhatsNewUI")
    chrome_options.add_argument("--window-size=1150,900")
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    # chrome_options.add_argument(f'--profile-directory=default')

    # chrome_options.add_argument(f'--user-data-dir=/Users/hecmay/Library/Application Support/Chrome')

    chrome_service = ChromeService(ChromeDriverManager().install())
    session = uc.Chrome(
        options=chrome_options, service=chrome_service, use_subprocess=True)

    session.get(
        "https://apple.stackexchange.com/questions/28928/what-is-the-macos-equivalent-to-windows-appdata-folder")
    # session.get("https://baidu.com") 
    time.sleep(0.5)
    session.get("https://google.com")
    time.sleep(0.5)
    session.get("https://bing.com")
    time.sleep(20)


main()
