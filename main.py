from ClosestStations import StationManager
from TrainStationDatabaseCreation import StationDatabaseManager
from RealRouteFinder import RealRouteFinder


# Przykład użycia
if __name__ == "__main__":
    route_finder = RealRouteFinder()

    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)

    area = "Polska"
    station_manager.fetch_and_store_stations(area)

    start_address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    destination_address = "valeo chrzanów"

    start_coords = station_manager.get_coordinates(start_address)
    end_coords = station_manager.get_coordinates(destination_address)

    if start_coords and end_coords:
        start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations=3)
        end_stations = station_manager.find_nearest_stations(end_coords[0], end_coords[1], num_stations=3)

        date = "2025-02-19"
        time = "09:00"

        connections = route_finder.find_connections(start_stations, end_stations, date, time)
        for connection in connections:
            print(f"Połączenie z {connection['start_station']} do {connection['end_station']}:")
            route = connection['route']
            print(f" - Połączenie: {route['departure']} -> {route['arrival']}, Czas trwania: {route['duration']}")
    else:
        print("Nie udało się uzyskać współrzędnych dla podanych adresów.")