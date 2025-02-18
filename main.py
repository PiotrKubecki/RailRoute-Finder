from ClosestStations import StationManager
from TrainStationDatabaseCreation import StationDatabaseManager

if __name__ == "__main__":
    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)

    area = "Polska"  # Możesz określić inne obszary według potrzeby
    station_manager.fetch_and_store_stations(area)

    address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    coordinates = station_manager.get_coordinates(address)
    if coordinates:
        print(f"Uzyskane współrzędne: {coordinates}")
        nearest_stations = station_manager.find_nearest_stations(coordinates[0], coordinates[1], num_stations=3)
        print("Najbliższe stacje:", nearest_stations)
    else:
        print("Nie udało się uzyskać współrzędnych dla podanego adresu.")
