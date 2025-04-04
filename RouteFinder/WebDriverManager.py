import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options


class WebDriverManager:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    def start_driver(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def wait_for_element(self, by_strategy, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            ec.presence_of_element_located((by_strategy, locator))
        )

    def click_element(self, by_strategy, locator, timeout=20):
        element = WebDriverWait(self.driver, timeout).until(
            ec.element_to_be_clickable((by_strategy, locator))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.1)
        element.click()

    def enter_text(self, by_strategy, locator, text, timeout=10):
        element = self.wait_for_element(by_strategy, locator, timeout)
        element.clear()
        element.send_keys(text)
