import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
import logging
from WebDriverManager import WebDriverManager


class RealRouteFinder:
    def __init__(self):
        self.driver_path = self.get_chrome_driver_path()
        self.driver_manager = WebDriverManager(self.driver_path)

    def get_chrome_driver_path(self):
        driver_path = "chromedriver.exe"
        if not os.path.exists(driver_path):
            driver_path = ChromeDriverManager().install()
        return driver_path

    def set_date_by_clicking(self, date_string):
        target_date = datetime.strptime(date_string, "%Y-%m-%d").date()
        current_date = datetime.now().date()
        days_difference = (target_date - current_date).days

        button_xpath = '//*[@id="wyszukiwarka"]/form/div[8]/div[2]/div[2]/button[2]'
        date_change_button = self.driver_manager.wait_for_element(By.XPATH, button_xpath)
        self.driver_manager.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_change_button)
        time.sleep(0.5)

        if not date_change_button.is_enabled() or not date_change_button.is_displayed():
            return

        for _ in range(abs(days_difference)):
            date_change_button.click()
            time.sleep(0.1)

    def select_checkboxes(self, options_to_select):
        checkbox_xpaths = {
            'direct_connections_only': "//*[@id='collapseOne']/fieldset/div[1]/div/label[2]/div",
            'bicycle transport': "//*[@id='collapseOne']/fieldset/div[2]/div/label[2]/div",
            'facilities for disabled people': "//*[@id='collapseOne']/fieldset/div[3]/div/label[2]/div",
            'facilities for people with children': "//*[@id='collapseOne']/fieldset/div[4]/div/label[2]/div"
        }
        for option in options_to_select:
            if option in checkbox_xpaths:
                xpath = checkbox_xpaths[option]
                checkbox = self.driver_manager.wait_for_element(By.XPATH, xpath)
                if not checkbox.is_selected():
                    checkbox.click()

    def anchor_close(self):
        self.driver_manager.click_element(By.XPATH, "//*[@id='yb_anchor_wrapper']/span", timeout=10)

    def find_real_routes(self, start_station, end_station, date_string, time_value, checkbox_options):
        self.driver_manager.start_driver()
        self.driver_manager.driver.get("https://rozklad-pkp.pl")

        try:
            self.driver_manager.click_element(By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[2]")
            self.driver_manager.enter_text(By.XPATH, "//*[@id='from-station']", start_station)
            self.driver_manager.enter_text(By.XPATH, "//*[@id='to-station']", end_station)
            self.driver_manager.enter_text(By.XPATH, "//*[@id='hour']", time_value)

            self.set_date_by_clicking(date_string)
            self.anchor_close()

            if checkbox_options:
                self.select_checkboxes(checkbox_options)
            self.driver_manager.click_element(By.XPATH, "//*[@id='singlebutton']")

            connections = []
            no_results_xpath = "//*[@id='content']/div[2]/div[1]/div[2]/table/tbody/tr/td/text()"
            try:
                no_results_element = WebDriverWait(self.driver_manager.driver, 5).until(
                    ec.presence_of_element_located((By.XPATH, no_results_xpath))
                )
                if "niestety" in no_results_element.text:
                    return None

            except Exception as e:
                logging.warning(f"Nie znaleziono elementu no-results lub wystąpił błąd: {e}")

            for i in range(1, 3):
                try:
                    base_xpath = f"//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-{i}']"
                    transfer_amount = self.driver_manager.wait_for_element(By.XPATH, base_xpath + "/td[6]",
                                                                           timeout=2).text
                    duration = self.driver_manager.wait_for_element(By.XPATH, base_xpath + "/td[5]", timeout=2).text
                    departure_time = self.driver_manager.wait_for_element(
                        By.XPATH, base_xpath + "/td[4]/p[1]/span[1]/span[3]", timeout=2).text
                    connections.append({
                        'transfers': transfer_amount,
                        'departure': departure_time,
                        'duration': duration
                    })
                except Exception as e:
                    logging.warning(f"Error occurred while fetching data for connection {i}: {e}")

            return connections if connections else None
        finally:
            self.driver_manager.stop_driver()

    def find_connections(self, start_stations, end_stations, date_string, time_value, checkbox_options=None):
        all_connections = []
        for start_station in start_stations:
            for end_station in end_stations:
                routes = self.find_real_routes(start_station[0], end_station[0], date_string, time_value,
                                               checkbox_options)
                if routes:
                    for route in routes:
                        connection_info = {
                            'start_station': start_station[0],
                            'end_station': end_station[0],
                            **route
                        }
                        all_connections.append(connection_info)

        return all_connections
