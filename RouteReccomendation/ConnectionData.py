import csv

class ConnectionManager:
    def __init__(self):
        self.connections = []

    def add_connection(self, route_id, from_city, to_city, transfers, departure_time, duration):
        connection = {
            "route_id": route_id,
            "from_city": from_city,
            "to_city": to_city,
            "transfers": transfers,
            "departure_time": departure_time,
            "duration": duration
        }
        self.connections.append(connection)

    def get_all_connections(self):
        return self.connections

    def save_to_csv(self, file_name):
        keys = self.connections[0].keys()
        with open(file_name, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.connections)


