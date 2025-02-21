import logging
from ClosestStations import StationManager
from TrainStationDatabaseCreation import StationDatabaseManager
from RealRouteFinder import RealRouteFinder

# Configure logging
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

    # Initialize components
    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)
    route_finder = RealRouteFinder()

    # Fetch and store stations if not already fetched
    area = "Polska"
    query_result = db_manager.execute_query("SELECT COUNT(*) FROM stations")
    if query_result and query_result[0][0] == 0:
        logging.info(f"Fetching and storing stations for area: {area}")
        station_manager.fetch_and_store_stations(area)
    else:
        logging.info(f"Stations already fetched and stored.")

    # User input addresses
    start_address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    destination_address = "valeo chrzanów"

    # Get coordinates
    start_coords = station_manager.get_coordinates(start_address)
    end_coords = station_manager.get_coordinates(destination_address)

    if start_coords and end_coords:
        # Find nearest stations
        num_stations = 3
        start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations)
        end_stations = station_manager.find_nearest_stations(end_coords[0], end_coords[1], num_stations)

        date = "2025-02-19"
        time = "09:00"

        # Find connections
        connections = route_finder.find_connections(start_stations, end_stations, date, time)

        # Output results
        if connections:
            print("Otrzymane połączenia:")
            for connection in connections:
                print(f"Połączenie z {connection['start_station']} do {connection['end_station']}:")
                print(
                    f" - Przesiadki: {connection['transfers']}, Odjazd: {connection['departure']}, Czas trwania: {connection['duration']}"
                )
        else:
            print("Nie znaleziono połączeń dla podanych parametrów.")
    else:
        print("Nie udało się uzyskać współrzędnych dla podanych adresów.")

    # Close resources
    route_finder.close_driver()
    db_manager.close_db()
    logging.info("Route finding process completed.")

if __name__ == "__main__":
    main()
