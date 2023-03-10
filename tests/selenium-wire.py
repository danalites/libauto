from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import time
options = {
    'proxy': {
        'https': 'https://lrhrhnil:3iu0982joqa2@IP:PORT',
    }
}
chrome_service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(seleniumwire_options=options, service=chrome_service)
driver.get('https://httpbin.org/ip')

time.sleep(5)
driver.quit()
