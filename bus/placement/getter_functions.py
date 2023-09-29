import random
import csv

def get_bus_station_location(file_path):
    """
    Extracts the latitude, longitude and name of the bus stations from the csv file
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
        coordinates[n] = [lat,lon]
    
    return coordinates


def select_bus_station(coordinates: dict, start=1, end=20, lat=40.769033, lon=-73.969649):
    """
    Selects bus stations from provided stations within the specified distance

    Parameters
    ----------
    coordinates : dict
        Dictionary containing the latitude and longitude of the bus stations
    start : int
        Starting distance from the Central Park with latitude and longitude of 40.769033, -73.969649. (default)
    end : int
        Ending distance from the Central Park with latitude and longitude of 40.769033, -73.969649. (default)

    Returns
    -------
    selected_coordinates : dict
        Dictionary containing the latitude and longitude of the selected bus stations
    """
    selected_coordinates = {}
    for k,v in coordinates.items():
        if (v[0]-lat)**2 + (v[1]+lon)**2 >= start/100 and (v[0]-lat)**2 + (v[1]+lon)**2 <= end/100:
            selected_coordinates[k] = v
    
    return selected_coordinates

def get_station_distance(file):
    """
    Extracts the distance of the bus stations from the csv file
    """
    stations_dic = {}

    with open(file, "r") as input_file:
        next(input_file, None)
        for line in input_file:
            fields = line.strip().split(",")
            start = fields[0]
            end = fields[1]
            duration = float(fields[2])
            key = (start, end)
            stations_dic[key] = duration

    return stations_dic

# calculate the f and g for each station
# f is the number of people getting off at the station
# g is the distance from the nearest touristic site

def get_no_of_people_at_station(selected_coordinates):
    pop_at_station = {}
    with open("./data/station_pop_clean.csv", "r") as input_file:
        next(input_file, None)
        for line in input_file:
            fields = line.strip().split(",")
            station = fields[1]
            pop = float(fields[4])
            if station in selected_coordinates.keys():
                pop_at_station[station] = pop
    
    return pop_at_station

def get_distance_from_nearest_site(selected_coordinates):
    distance_from_site = {}
    with open("./data/bus_metro_distance.csv", "r") as input_file:
        next(input_file, None)
        for line in input_file:
            fields = line.strip().split(",")
            station = fields[0]
            distance = float(fields[2])
            if station in selected_coordinates.keys():
                distance_from_site[station] = distance
    
    return distance_from_site

def get_delay_from_nearest_station(selected_coordinates):
    delay_from_station = {}
    with open("./data/metro_delay.csv", "r") as input_file:
        next(input_file, None)
        for line in input_file:
            fields = line.strip().split(",")
            station = fields[1]
            delay = float(fields[3])
            if station in selected_coordinates.keys():
                delay_from_station[station] = delay
    
    return delay_from_station

def normalize(dic):
    max_value = max(dic.values())
    min_value = min(dic.values())
    for key in dic.keys():
        dic[key] = (dic[key] - min_value) / (max_value - min_value)
    return dic