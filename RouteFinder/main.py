import logging
from datetime import datetime

from RouteFinder.ClosestStations import StationManager
from RouteReccomendation.ConnectionData import ConnectionManager
from TrainStationDatabaseCreation import StationDatabaseManager
from RouteFinder.RealRouteFinder import RealRouteFinder

def main():
    logging.info("Starting the route finding process.")

    db_manager = StationDatabaseManager()
    station_manager = StationManager(db_manager)
    route_finder = RealRouteFinder()
    connection_manager = ConnectionManager()

    area = "Polska"
    query_result = db_manager.execute_query("SELECT COUNT(*) FROM stations")
    if query_result and query_result[0][0] == 0:
        logging.info(f"Fetching and storing stations for area: {area}")
        station_manager.fetch_and_store_stations(area)
    else:
        logging.info(f"Stations already fetched and stored.")

    start_address = "Jagiełły 31b/10, Siemianowice Śląskie, Polska"
    destination_address = "Doki 1, 80-863 Gdańsk"

    start_coords = station_manager.get_coordinates(start_address)
    end_coords = station_manager.get_coordinates(destination_address)

    if start_coords and end_coords:
        num_stations = 3
        start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations)
        end_stations = station_manager.find_nearest_stations(end_coords[0], end_coords[1], num_stations)

        date = "2025-03-03"
        time = "15:00"
        user_departure_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        checkbox_options = [
            'direct_connections_only',

            'bicycle transport'
            # 'facilities for disabled people'
            # 'facilities for people with children'
        ]

        route_id = 1
        connections = route_finder.find_connections(start_stations, end_stations, date, time,
                                                    checkbox_options=checkbox_options)

        if connections:
            print("Otrzymane połączenia:")
            for connection in connections:
                train_departure_time = datetime.strptime(connection['departure'], "%H:%M")
                waiting_time = (train_departure_time - user_departure_time).total_seconds() / 60
                if waiting_time < 0:
                    waiting_time += 24 * 60

                print(f"Połączenie z {connection['start_station']} do {connection['end_station']}:")
                print(
                    f" - Przesiadki: {connection['transfers']}, Odjazd: {connection['departure']}, Czas trwania: {connection['duration']}")
                connection_manager.add_connection(
                    route_id,
                    connection['start_station'],
                    connection['end_station'],
                    connection['transfers'],
                    waiting_time,
                    connection['duration']
                )
        else:
            print("Nie znaleziono połączeń dla podanych parametrów.")
    else:
        print("Nie udało się uzyskać współrzędnych dla podanych adresów.")

    connection_manager.save_to_csv('connections.csv')
    db_manager.close_db()
    logging.info("Route finding process completed.")


if __name__ == "__main__":
    main()
