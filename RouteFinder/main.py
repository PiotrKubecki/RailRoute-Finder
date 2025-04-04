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

    start_address = "Strumykowa 2, 67-200 Głogów"
    destination_address = "Jana Długosza 59-75, 51-162 Wrocław"

    start_coords = station_manager.get_coordinates(start_address)
    end_coords = station_manager.get_coordinates(destination_address)

    if start_coords and end_coords:
        num_stations = 3
        start_stations = station_manager.find_nearest_stations(start_coords[0], start_coords[1], num_stations)
        end_stations = station_manager.find_nearest_stations(end_coords[0], end_coords[1], num_stations)

        date = "2025-04-2"
        time = "15:00"
        user_departure_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        checkbox_options = [
            # 'direct_connections_only',

            # 'bicycle transport'
            # 'facilities for disabled people'
            # 'facilities for people with children'
        ]

        route_id = 16
        connections = route_finder.find_connections(start_stations, end_stations, date, time, checkbox_options=checkbox_options)

        distances_from_start = {entry[0]: entry[3] for entry in start_stations}
        distances_to_destination = {entry[0]: entry[3] for entry in end_stations}

        if connections:
            print("Connections found:")
            for connection in connections:

                try:
                    train_departure_time = datetime.strptime(connection['departure'], "%H:%M")
                except ValueError as e:
                    logging.warning(f"Invalid departure time format for connection: {connection}. Error: {e}")
                    continue

                # Match departure time with user's input
                train_departure_time = user_departure_time.replace(hour=train_departure_time.hour, minute=train_departure_time.minute)

                if train_departure_time < user_departure_time:
                    continue  # Skip connections before user departure time

                # Calculate waiting time
                waiting_time = (train_departure_time - user_departure_time).total_seconds() / 60

                print(f"Connection from {connection['start_station']} to {connection['end_station']}:")
                print(
                    f" - Transfers: {connection['transfers']}, Waiting time: {waiting_time:.2f} minutes, Duration: {connection['duration']}")

                # Add connection to manager with default distance values
                if connection:
                    connection_manager.add_connection(
                        route_id,
                        connection['start_station'],
                        connection['end_station'],
                        connection['transfers'],
                        waiting_time,
                        connection['duration'],
                        distances_from_start[connection['start_station']],  # Default distance from start
                        distances_to_destination[connection['end_station']]   # Default distance to destination
                    )
        else:
            print("No connections found for the given parameters.")

        connection_manager.save_to_csv('connections.csv')

    else:
        print("Coordinates for the specified addresses could not be obtained.")


    db_manager.close_db()
    logging.info("Route finding process completed.")


if __name__ == "__main__":
    main()
