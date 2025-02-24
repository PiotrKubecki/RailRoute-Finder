from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

class RealRouteFinder:
    def __init__(self):
        self.driver_path = self.get_chrome_driver_path()
        self.driver = None

    def get_chrome_driver_path(self):
        driver_path = "chromedriver.exe"
        if not os.path.exists(driver_path):
            driver_path = ChromeDriverManager().install()
        return driver_path

    def start_driver(self):
        self.driver = webdriver.Chrome(service=Service(self.driver_path))
        # Optionally, add Chrome options if needed
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Run in headless mode
        # self.driver = webdriver.Chrome(service=Service(self.driver_path), options=options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def wait_for_element(self, by_strategy, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by_strategy, locator))
        )

    def click_element(self, by_strategy, locator, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by_strategy, locator))
        )
        element.click()

    def enter_text(self, by_strategy, locator, text, timeout=10):
        element = self.wait_for_element(by_strategy, locator, timeout)
        element.clear()
        element.send_keys(text)

    def find_real_routes(self, start_station, end_station, date, time):
        # Initialize the browser
        self.start_driver()
        self.driver.get("https://rozklad-pkp.pl")

        # Accept cookies
        try:
            self.click_element(By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[2]")
        except:
            print("Nie udało się znaleźć przycisku akceptacji cookies.")

        # Input start station
        self.enter_text(By.XPATH, "//*[@id='from-station']", start_station)

        # Input end station
        self.enter_text(By.XPATH, "//*[@id='to-station']", end_station)

        # # Input date
        # self.enter_text(By.XPATH, "//*[@id='date']", date)

        # Input time
        self.enter_text(By.XPATH, "//*[@id='hour']", time)

        # Close any anchors if they appear
        self.anchor_close()

        # Click the search button
        self.click_element(By.XPATH, "//*[@id='singlebutton']")

        # # Close any anchors after search
        # self.anchor_close()

        # Analyze search results
        connections = []
        try:
            # Retrieve transfer amount
            transfer_amount = self.wait_for_element(
                By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-1']/td[6]"
            ).text

            # Retrieve duration
            duration = self.wait_for_element(
                By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-1']/td[5]"
            ).text

            # Retrieve departure time
            departure_time = self.wait_for_element(
                By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-1']/td[4]/p[1]/span[1]/span[3]"
            ).text

            connections.append({
                'transfers': transfer_amount,
                'departure': departure_time,
                'duration': duration
            })
        except:
            print("Nie udało się znaleźć informacji o połączeniu.")

        # Close the browser
        self.stop_driver()

        if connections:
            return connections[0]  # Return the first connection
        else:
            return None

    def find_connections(self, start_stations, end_stations, date, time):
        all_connections = []
        for start_station in start_stations:
            for end_station in end_stations:
                route = self.find_real_routes(start_station[0], end_station[0], date, time)
                if route:
                    connection_info = {
                        'start_station': start_station[0],
                        'end_station': end_station[0],
                        **route
                    }
                    all_connections.append(connection_info)
        return all_connections

    def anchor_close(self):
        try:
            self.click_element(By.XPATH, "//*[@id='yb_anchor_wrapper']/span", timeout=5)
        except:
            pass  # If the element isn't found, do nothing
