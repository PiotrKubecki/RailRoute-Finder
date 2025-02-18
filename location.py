import sqlite3
import overpy
from geopy.geocoders import Nominatim
import math

def create_station_db():
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute('''
        DROP TABLE IF EXISTS stations
    ''')
    cursor.execute('''
        CREATE TABLE stations (
            id INTEGER PRIMARY KEY,
            name TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_station(name, lat, lon):
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO stations (name, latitude, longitude)
        VALUES (?, ?, ?)
    ''', (name, float(lat), float(lon)))  # Konwersja lat i lon na float
    conn.commit()
    conn.close()

def fetch_and_store_stations(area):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    area[name="{area}"]->.searchArea;
    (
      node["railway"="station"](area.searchArea);
      way["railway"="station"](area.searchArea);
      relation["railway"="station"](area.searchArea);
    );
    out center;
    """
    result = api.query(query)
    for node in result.nodes:
        name = node.tags.get('name', 'Unknown')
        lat = node.lat
        lon = node.lon
        add_station(name, lat, lon)

def get_coordinates(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    print("Nie udało się uzyskać współrzędnych dla podanego adresu.")
    return None

def distance(lat1, lon1, lat2, lon2):
    r = 6371  # Promień Ziemi w kilometrach
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

def find_nearest_stations(lat, lng, num_stations=8):
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, latitude, longitude FROM stations")
    all_stations = cursor.fetchall()
    city_stations = {}
    for station in all_stations:
        station_lat = station[1]
        station_lon = station[2]
        dist = distance(lat, lng, station_lat, station_lon)
        city = station[0].split()[0]  # Podstawowe rozwiązanie do filtrowania na podstawie nazwy stacji
        if city not in city_stations or dist < city_stations[city][3]:
            city_stations[city] = (station[0], station_lat, station_lon, dist)
    # Pobierz najbliższą stację z każdego miasta
    stations = list(city_stations.values())
    stations.sort(key=lambda x: x[3])  # Sortowanie według odległości
    return stations[:num_stations]

def display_stations():
    conn = sqlite3.connect('stations.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, latitude, longitude FROM stations ORDER BY name ASC")  # Sortowanie według nazwy rosnąco
    all_stations = cursor.fetchall()
    conn.close()

    if all_stations:
        print("Baza danych stacji kolejowych:")
        for station in all_stations:
            print(f"Nazwa: {station[0]}, Lat: {station[1]}, Lon: {station[2]}")
    else:
        print("Baza danych jest pusta.")

# Przykład użycia
create_station_db()
area = "Polska"  # Możesz określić inne obszary według potrzeby
fetch_and_store_stations(area)

address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
coordinates = get_coordinates(address)
if coordinates:
    print(f"Uzyskane współrzędne: {coordinates}")
    nearest_stations = find_nearest_stations(coordinates[0], coordinates[1], num_stations=8)
    print("Najbliższe stacje:", nearest_stations)
    display_stations()  # Wyświetlanie zawartości bazy danych
else:
    print("Nie udało się uzyskać współrzędnych dla podanego adresu.")
