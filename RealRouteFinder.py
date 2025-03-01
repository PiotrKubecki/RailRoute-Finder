import os
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager


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
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(service=Service(self.driver_path), options=options)
        self.driver.maximize_window()

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def wait_for_element(self, by_strategy, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            ec.presence_of_element_located((by_strategy, locator))
        )

    def click_element(self, by_strategy, locator, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            ec.element_to_be_clickable((by_strategy, locator))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        element.click()

    def enter_text(self, by_strategy, locator, text, timeout=10):
        element = self.wait_for_element(by_strategy, locator, timeout)
        element.clear()
        element.send_keys(text)

    def set_date_by_clicking(self, date_string):
        try:
            target_date = datetime.strptime(date_string, "%Y-%m-%d").date()
        except Exception as e:
            print("Błąd przy przetwarzaniu daty wejściowej:", e)
            return

        current_date = datetime.now().date()
        days_difference = (target_date - current_date).days

        button_xpath = '//*[@id="wyszukiwarka-wyniki"]/div[3]/div[1]/div/button[2]'

        try:
            date_change_button = self.wait_for_element(By.XPATH, button_xpath)
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", date_change_button)
            time.sleep(0.5)

            if not date_change_button.is_enabled():
                print("Przycisk zmiany daty nie jest aktywny.")
                return
            if not date_change_button.is_displayed():
                print("Przycisk zmiany daty nie jest widoczny.")
                return

            for _ in range(abs(days_difference)):
                print(f"Kliknięcie przycisku: {_ + 1} z {abs(days_difference)}")
                date_change_button.click()
                time.sleep(0.1)  # Small delay between clicks

            print(f"Ustawiona data: {target_date}")
        except Exception as e:
            print(f"Błąd przy klikaniu przycisku: {e}")

    def select_checkboxes(self, options_to_select):
        checkbox_xpaths = {
            'direct_connections_only': "//*[@id='collapseOne']/fieldset/div[1]/div/label[2]/div",
            'bicycle transport': "//*[@id='collapseOne']/fieldset/div[2]/div/label[2]/div",
            'facilities for disabled people': "//*[@id='collapseOne']/fieldset/div[3]/div/label[2]/div",
            'facilities for people with children': "//*[@id='collapseOne']/fieldset/div[4]/div/label[2]/div"
        }
        try:
            for option in options_to_select:
                if option in checkbox_xpaths:
                    xpath = checkbox_xpaths[option]
                    checkbox = self.wait_for_element(By.XPATH, xpath)
                    if not checkbox.is_selected():
                        checkbox.click()
                else:
                    print(f"Opcja '{option}' nie jest rozpoznawana.")
        except Exception as e:
            print(f"Błąd podczas zaznaczania checkboxów: {e}")

    def anchor_close(self):
        try:
            self.click_element(By.XPATH, "//*[@id='yb_anchor_wrapper']/span", timeout=10)
        except Exception:
            pass

    def find_real_routes(self, start_station, end_station, date_string, time_value, checkbox_options):
        self.start_driver()
        self.driver.get("https://rozklad-pkp.pl")

        try:
            self.click_element(By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[2]")
        except Exception:
            print("Nie udało się znaleźć przycisku akceptacji cookies.")

        self.enter_text(By.XPATH, "//*[@id='from-station']", start_station)
        self.enter_text(By.XPATH, "//*[@id='to-station']", end_station)
        self.enter_text(By.XPATH, "//*[@id='hour']", time_value)

        self.anchor_close()
        # self.set_date_by_clicking(date_string)

        if checkbox_options:
            self.select_checkboxes(checkbox_options)
        self.click_element(By.XPATH, "//*[@id='singlebutton']")

        connections = []
        try:
            no_results_xpath = "//div[contains(@class, 'no-result')]"
            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.XPATH, no_results_xpath))
            )
            print("Brak dostępnych połączeń dla podanych parametrów.")
            self.stop_driver()
            return None
        except Exception:
            pass

        for i in range(1, 3):
            try:
                base_xpath = f"//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-{i}']"
                transfer_amount = self.wait_for_element(By.XPATH, base_xpath + "/td[6]").text
                duration = self.wait_for_element(By.XPATH, base_xpath + "/td[5]").text
                departure_time = self.wait_for_element(By.XPATH, base_xpath + "/td[4]/p[1]/span[1]/span[3]").text
                connections.append({
                    'transfers': transfer_amount,
                    'departure': departure_time,
                    'duration': duration
                })
            except Exception as e:
                print(f"Nie udało się pobrać danych dla połączenia {i}: {e}")

        self.stop_driver()
        return connections if connections else None

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
                else:
                    print(f"Brak połączenia z {start_station[0]} do {end_station[0]}")
        return all_connections
