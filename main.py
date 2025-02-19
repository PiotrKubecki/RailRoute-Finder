from ClosestStations import StationManager
from TrainStationDatabaseCreation import StationDatabaseManager

if __name__ == "__main__":
    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)

    area = "Polska"  # Możesz określić inne obszary według potrzeby
    station_manager.fetch_and_store_stations(area)

    start_address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    destination_address = "valeo chrzanów"

    start_coords = station_manager.get_coordinates(start_address)
    destination_coords = station_manager.get_coordinates(destination_address)
    if start_coords:
        print(f"Uzyskane współrzędne startu: {start_coords}")
        nearest_start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations=5)
        print("Najbliższe stacje na starcie:", nearest_start_stations)
    else:
        print("Nie udało się uzyskać współrzędnych dla podanego adresu startowego.")


    if destination_coords:
        print(f"Uzyskane współrzędne celu: {destination_coords}")
        nearest_end_stations = station_manager.find_nearest_stations(destination_coords[0], destination_coords[1],
                                                                     num_stations=5)
        print("Najbliższe stacje na końcu:", nearest_end_stations)
    else:
        print("Nie udało się uzyskać współrzędnych dla podanego adresu docelowego.")