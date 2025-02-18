import overpy
from geopy.geocoders import Nominatim
import math

class StationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def add_station(self, name, lat, lon):
        command = '''
            INSERT INTO stations (name, latitude, longitude)
            VALUES (?, ?, ?)
        '''
        self.db_manager.execute_command(command, (name, float(lat), float(lon)))  # Konwersja lat i lon na float

    def fetch_and_store_stations(self, area):
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
            self.add_station(name, lat, lon)

    def get_coordinates(self, address):
        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        print("Nie udało się uzyskać współrzędnych dla podanego adresu.")
        return None

    def distance(self, lat1, lon1, lat2, lon2):
        r = 6371  # Promień Ziemi w kilometrach
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    def find_nearest_stations(self, lat, lng, num_stations=5):
        query = "SELECT name, latitude, longitude FROM stations"
        all_stations = self.db_manager.execute_query(query)
        city_stations = {}
        for station in all_stations:
            station_lat = station[1]
            station_lon = station[2]
            dist = self.distance(lat, lng, station_lat, station_lon)
            city = station[0].split()[0]  # Podstawowe rozwiązanie do filtrowania na podstawie nazwy stacji
            if city not in city_stations or dist < city_stations[city][3]:
                city_stations[city] = (station[0], station_lat, station_lon, dist)
        # Pobierz najbliższą stację z każdego miasta
        stations = list(city_stations.values())
        stations.sort(key=lambda x: x[3])  # Sortowanie według odległości
        return stations[:num_stations]
