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

    def find_real_routes(self, start_station, end_station, date, time):
        # Inicjalizacja przeglądarki
        self.driver = webdriver.Chrome(service=Service(self.driver_path))
        self.driver.get("https://rozklad-pkp.pl")

        # Akceptowanie cookies
        try:
            accept_cookies_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[2]"))
            )
            accept_cookies_button.click()
        except:
            print("Nie udało się znaleźć przycisku akceptacji cookies.")

        # Oczekiwanie na element stacji początkowej i końcowej
        from_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='from-station']"))
        )
        from_input.clear()
        from_input.send_keys(start_station)

        # # Oczekiwanie na elementy daty i godziny
        # date_input = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "date"))
        # )
        # date_input.clear()
        # date_input.send_keys(date)

        time_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='hour']"))
        )
        time_input.clear()
        time_input.send_keys(time)


        to_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='to-station']"))
        )
        to_input.clear()
        to_input.send_keys(end_station)

        self.anchor_close()

        # Klikanie przycisku wyszukiwania
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='singlebutton']"))
        ).click()


        self.anchor_close()

        # Analizowanie wyników wyszukiwania
        connections = []

        transfer_amount = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C1-1']/td[6]"))
        ).text

        duration = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C1-1']/td[5]"))
        ).text

        departure_time = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C1-1']/td[4]/p[1]/span[1]/span[3]"))
        ).text

        connections.append({
            'transfers': transfer_amount,
            'departure':departure_time,
            'duration': duration
        })

        self.driver.quit()
        if connections:
            return connections[0]  # Zwróć pierwsze połączenie
        else:
            return None

    def find_connections(self, start_stations, end_stations, date, time):
        all_connections = []
        for start_station in start_stations:
            for end_station in end_stations:
                route = self.find_real_routes(start_station[0], end_station[0], date, time)
                if route:
                    all_connections.append({
                        'start_station': start_station[0],
                        'end_station': end_station[0],
                        'route': route
                    })
        return all_connections

    def anchor_close(self):
        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='yb_anchor_wrapper']/span"))
        )
        search_button.click()
