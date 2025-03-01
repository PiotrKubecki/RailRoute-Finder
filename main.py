import logging
from ClosestStations import StationManager
from TrainStationDatabaseCreation import StationDatabaseManager
from RealRouteFinder import RealRouteFinder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("route_finder.log"),
        logging.StreamHandler()
    ]
)


def main():
    logging.info("Starting the route finding process.")

    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)
    route_finder = RealRouteFinder()

    area = "Polska"
    query_result = db_manager.execute_query("SELECT COUNT(*) FROM stations")
    if query_result and query_result[0][0] == 0:
        logging.info(f"Fetching and storing stations for area: {area}")
        station_manager.fetch_and_store_stations(area)
    else:
        logging.info(f"Stations already fetched and stored.")

    start_address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    destination_address = "stocznia gdańska"

    start_coords = station_manager.get_coordinates(start_address)
    end_coords = station_manager.get_coordinates(destination_address)

    if start_coords and end_coords:
        num_stations = 3
        start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations)
        end_stations = station_manager.find_nearest_stations(end_coords[0], end_coords[1], num_stations)

        date = "2025-03-30"
        time = "4:00"

        checkbox_options = [
            'direct_connections_only',

            # 'bicycle transport'
            # 'facilities for disabled people'
            # 'facilities for people with children'
        ]

        connections = route_finder.find_connections(start_stations, end_stations, date, time,
                                                    checkbox_options=checkbox_options)

        if connections:
            print("Otrzymane połączenia:")
            for connection in connections:
                print(f"Połączenie z {connection['start_station']} do {connection['end_station']}:")
                print(
                    f" - Przesiadki: {connection['transfers']}, Odjazd: {connection['departure']}, Czas trwania: {connection['duration']}")
        else:
            print("Nie znaleziono połączeń dla podanych parametrów.")
    else:
        print("Nie udało się uzyskać współrzędnych dla podanych adresów.")

    db_manager.close_db()
    logging.info("Route finding process completed.")


if __name__ == "__main__":
    main()
