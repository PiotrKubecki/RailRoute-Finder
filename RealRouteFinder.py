from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
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
        # Opcjonalnie, dodaj opcje Chrome, jeśli potrzebujesz
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Uruchom w trybie headless
        # self.driver = webdriver.Chrome(service=Service(self.driver_path), options=options)

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
        element.click()

    def enter_text(self, by_strategy, locator, text, timeout=10):
        element = self.wait_for_element(by_strategy, locator, timeout)
        element.clear()
        element.send_keys(text)

    def select_checkboxes(self, options_to_select):
        # Mapping nazw opcji do ich XPaths
        checkbox_xpaths = {
            'direct_connections_only': "//*[@id='collapseOne']/fieldset/div[1]/div/label[2]/div",
            'bicycle transport': "//*[@id='collapseOne']/fieldset/div[2]/div/label[2]/div",
            'facilities for disabled people': "//*[@id='collapseOne']/fieldset/div[3]/div/label[2]/div",
            'facilities for people with children': "//*[@id=''collapseOne']/fieldset/div[4]/div/label[2]/div",
            # Dodaj inne opcje i ich XPaths w razie potrzeby
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

    def find_real_routes(self, start_station, end_station, date, time, checkbox_options):
        # Inicjalizacja przeglądarki
        self.start_driver()
        self.driver.get("https://rozklad-pkp.pl")

        # Akceptowanie cookies
        try:
            self.click_element(By.XPATH, "//*[@id='qc-cmp2-ui']/div[2]/div/button[2]")
        except:
            print("Nie udało się znaleźć przycisku akceptacji cookies.")

        # Wprowadź stację początkową
        self.enter_text(By.XPATH, "//*[@id='from-station']", start_station)

        # Wprowadź stację końcową
        self.enter_text(By.XPATH, "//*[@id='to-station']", end_station)

        # Wprowadź godzinę
        self.enter_text(By.XPATH, "//*[@id='hour']", time)

        # Zamknij ewentualne pop-upy
        self.anchor_close()

        # Zaznacz checkboxy przed wyszukiwaniem
        if checkbox_options:
            self.select_checkboxes(checkbox_options)

        # Kliknij przycisk wyszukiwania
        self.click_element(By.XPATH, "//*[@id='singlebutton']")

        # Analiza wyników wyszukiwania
        connections = []
        try:
            # Sprawdź, czy pojawiła się informacja o braku wyników
            no_results_xpath = "//div[contains(@class, 'no-result')]"
            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.XPATH, no_results_xpath))
            )
            print("Brak dostępnych połączeń dla podanych parametrów.")
            # Brak połączeń, zamknij przeglądarkę i zwróć None
            self.stop_driver()
            return None
        except:
            # Jeżeli nie znaleziono komunikatu o braku wyników, kontynuuj
            pass

        try:
            # Pobierz liczbę przesiadek
            transfer_amount = self.wait_for_element(
                By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-1']/td[6]"
            ).text

            # Pobierz czas trwania
            duration = self.wait_for_element(
                By.XPATH, "//*[@id='focus_guiVCtrl_connection_detailsOut_select_C0-1']/td[5]"
            ).text

            # Pobierz czas odjazdu
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
            # Nie udało się pobrać danych, zamknij przeglądarkę i zwróć None
            self.stop_driver()
            return None

        # Zamknij przeglądarkę
        self.stop_driver()

        if connections:
            return connections[0]  # Zwróć pierwsze połączenie
        else:
            return None

    def find_connections(self, start_stations, end_stations, date, time,checkbox_options=None):
        all_connections = []
        for start_station in start_stations:
            for end_station in end_stations:
                route = self.find_real_routes(start_station[0], end_station[0], date, time, checkbox_options)
                if route:
                    connection_info = {
                        'start_station': start_station[0],
                        'end_station': end_station[0],
                        **route
                    }
                    all_connections.append(connection_info)
                else:
                    print(f"Brak połączenia z {start_station[0]} do {end_station[0]}")
                    # Przejdź do następnej pary stacji
                    continue
        return all_connections

    def anchor_close(self):
        try:
            self.click_element(By.XPATH, "//*[@id='yb_anchor_wrapper']/span", timeout=10)
        except:
            pass  # Jeśli element nie zostanie znaleziony, nic nie rób
