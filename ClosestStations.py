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
        self.db_manager.execute_command(command, (name, float(lat), float(lon)))

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

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        earth_radius_km = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        haversine_formula = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)) * math.sin(dlon / 2) ** 2
        central_angle = 2 * math.atan2(math.sqrt(haversine_formula), math.sqrt(1 - haversine_formula))
        return earth_radius_km * central_angle

    def find_nearest_stations(self, lat, lon, num_stations=5):
        query = "SELECT name, latitude, longitude FROM stations"
        all_stations = self.db_manager.execute_query(query)
        distances = [
            (station[0], station[1], station[2], self.calculate_distance(lat, lon, station[1], station[2]))
            for station in all_stations
        ]

        # Sortowanie stacji według odległości
        distances.sort(key=lambda x: x[3])

        # Filtracja najbliższych stacji z różnych miast
        nearest_stations = {}
        for station in distances:
            city = station[0].split()[0]
            if city not in nearest_stations:
                nearest_stations[city] = station
            if len(nearest_stations) >= num_stations:
                break

        return list(nearest_stations.values())[:num_stations]
