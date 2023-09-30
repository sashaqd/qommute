import csv
import random

class GetterFunctions:
    def __init__(self):
        self.coordinates = self.get_data_from_csv("./data/bus_station_location.csv")
        self.selected_coordinates = self.get_selected_locations(self.coordinates)
        self.station_distances = self.get_distance_between_stations()
        self.pop_at_station = self.get_no_of_people_at_station(self.selected_coordinates)
        self.distance_from_metro = self.get_distance_from_farthest_metro(self.selected_coordinates)
        self.delay_from_station = self.get_delay_from_nearest_station(self.selected_coordinates)

    def get_data_from_csv(self, file_path):
        """
        Takes a csv file path as input and returns a dictionary of coordinates

        Parameters
        ----------
        file_path : str
            The path to the csv file

        Returns
        -------
        coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        """
        # Initialize empty lists to store the extracted values
        latitudes = []
        longitudes = []
        names = []

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            # Loop over each row in the csv using reader object
            for row in reader:
                # row variable is a list that represents a row in csv
                latitude = float(row[1])
                longitude = float(row[2])
                name = row[0]
                # Append the values to the respective lists
                latitudes.append(latitude)
                longitudes.append(longitude)
                names.append(name)

        coordinates = {}
        for lat, lon, n in zip(latitudes, longitudes, names):
            coordinates[n] = (lat, lon)
        
        return coordinates

    def get_selected_locations(self, coordinates: dict, n=20, start=1, end=20, lat=40.76903, lon=-73.969649):
        """
        Randomly selects n locations from the coordinates dictionary

        Parameters
        ----------
        coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        n : int
            The number of locations to be selected
        start : int
            The start distance from the center of the map
        end : int
            The end distance from the center of the map

        Returns
        -------
        selected_coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        """
        selected_coordinates = {}
        for k,v in coordinates.items():
            if (v[0]-lat)**2 + (v[1]-lon)**2 >= start/100 and (v[0]-lat)**2 + (v[1]-lon)**2 <= end/100:
                selected_coordinates[k] = v
        
        random.seed(42)
        selected_coordinates = dict(random.sample(list(selected_coordinates.items()), n))

        return selected_coordinates

    def get_distance_between_stations(self, file_path = "./data/station_distance.csv"):
        """
        Takes a csv file path as input and returns a dictionary of distances between stations

        Parameters
        ----------
        file_path : str
            The path to the csv file

        Returns
        -------
        station_distances : dict
            A dictionary of distances between stations with the name of the city as key and a tuple of latitude and longitude as value
        """
        # Initialize empty lists to store the extracted values
        station_distances = {}

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            # Loop over each row in the csv using reader object
            for row in reader:
                # row variable is a list that represents a row in csv
                start = row[0]
                end = row[1]
                distance = float(row[2])
                # Append the values to the respective lists
                station_distances[(start, end)] = distance
        
        return station_distances

    def get_no_of_people_at_station(self, selected_coordinates: dict, file_path: str = "./data/station_pop_clean.csv"):
        """
        Takes a csv file path as input and returns a dictionary of distances between stations

        Parameters
        ----------
        selected_coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        file_path : str
            The path to the csv file

        Returns
        -------
        pop_at_station : dict
            A dictionary of distances between stations with the name of the city as key and a tuple of latitude and longitude as value
        """
        
        pop_at_station = {}
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            # Loop over each row in the csv using reader object
            for row in reader:
                # row variable is a list that represents a row in csv
                station = row[1]
                pop = float(row[3])
                # Append the values to the respective lists
                if station in selected_coordinates.keys():
                    pop_at_station[station] = pop
        
        return pop_at_station

    def get_distance_from_farthest_metro(self, selected_coordinates: dict, file_path: str = "./data/bus_metro_distance.csv"):
        """
        Takes a csv file path as input and returns a dictionary of distances between stations

        Parameters
        ----------
        selected_coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        file_path : str
            The path to the csv file

        Returns
        -------
        pop_at_station : dict
            A dictionary of distances between stations with the name of the city as key and a tuple of latitude and longitude as value
        """
        
        distance_from_metro = {}
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            # Loop over each row in the csv using reader object
            for row in reader:
                # row variable is a list that represents a row in csv
                station = row[0]
                distance = float(row[2])
                # Append the values to the respective lists
                if station in selected_coordinates.keys():
                    distance_from_metro[station] = distance
        
        return distance_from_metro

    def get_delay_from_nearest_station(self, selected_coordinates: dict, file_path: str = "./data/metro_delay.csv"):
        """
        Takes a csv file path as input and returns a dictionary of distances between stations

        Parameters
        ----------
        selected_coordinates : dict
            A dictionary of coordinates with the name of the city as key and a tuple of latitude and longitude as value
        file_path : str
            The path to the csv file

        Returns
        -------
        pop_at_station : dict
            A dictionary of distances between stations with the name of the city as key and a tuple of latitude and longitude as value
        """
        
        delay_from_station = {}
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            # Loop over each row in the csv using reader object
            for row in reader:
                # row variable is a list that represents a row in csv
                station = row[1]
                delay = float(row[3])
                # Append the values to the respective lists
                if station in selected_coordinates.keys():
                    delay_from_station[station] = delay
        
        return delay_from_station

    def normalize(self, dic: dict):
        """
        Takes a dictionary as input and returns a dictionary of normalized values

        Parameters
        ----------
        dic : dict
            A dictionary of values

        Returns
        -------
        dic : dict
            A dictionary of normalized values
        """
        max_value = max(dic.values())
        min_value = min(dic.values())
        for key in dic.keys():
            dic[key] = (dic[key] - min_value) / (max_value - min_value)
        return dic