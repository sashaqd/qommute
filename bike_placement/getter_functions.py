import random
import csv
from shapely.wkt import loads
import requests

def get_train_station_location(file_path):
    """
    Extracts the latitude, longitude and name of the train stations from the csv file
    """

    def parse_csv_file(file_path = 'data/DOITT_SUBWAY_STATION_01_13SEPT2010.csv'):
        # Initialize empty lists to store the extracted values
        latitudes = []
        longitudes = []
        names = []

        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row if present

            for row in reader:
                # Extract the desired fields
                url = row[0]
                object_id = row[1]
                name = row[2]
                geom = loads(row[3])  # Parse the WKT geometry into a Shapely object
                line = row[4]
                notes = row[5]

                # Extract latitude and longitude from the Shapely point
                latitude = geom.y
                longitude = geom.x

                # Append the values to the respective lists
                latitudes.append(latitude)
                longitudes.append(longitude)
                names.append(name)

        return latitudes, longitudes, names

    # Call the function to parse the data from the file
    latitudes, longitudes, names = parse_csv_file(file_path)

    coordinates = {}

    for lat, lon, n in zip(latitudes, longitudes, names):
        coordinates[n] = [lat,lon]

    
    return coordinates


def calculate_distance_from_api():
    # # Create and write to the CSV file
    # with open("/content/output.csv", mode="w", newline="") as file:
    #       writer = csv.writer(file)
    #       writer.writerow(["start", "end", "duration (mins)"])


    # with open("/content/output.csv", mode="a", newline="") as file:
    #     writer = csv.writer(file)

    #     for start in coordinates.items():
    #       start_lat = start[1][0]
    #       start_lon = start[1][1]
    #       start_name = start[0]
    #       print(start_name)
    #       for end in coordinates.items():

    #         end_name = end[0]
    #         if end_name == start_name:
    #           continue

    #         end_lat = end[1][0]
    #         end_lon = end[1][1]

    #         url = f"https://api.mapbox.com/directions/v5/mapbox/cycling/{start_lon}%2C{start_lat}%3B{end_lon}%2C{end_lat}?alternatives=false&annotations=distance%2Cduration&continue_straight=true&geometries=geojson&overview=full&steps=false&access_token=pk.eyJ1Ijoic2FzaGEtc3NtOTk2MCIsImEiOiJjbG4wcm9saG8xc3duMmlxd3pjY2MybDcyIn0.ol8PlZNYBX_XbtBu8I3igw"

    #         try:
    #             r = requests.get(url)
    #             r.raise_for_status()  # Raise an exception for bad response status
    #             dur = r.json()['routes'][0]['duration'] / 60  # Duration in minutes

    #         # Write the record to the CSV file immediately after receiving the response
    #             writer.writerow([start_name, end_name, dur])
    #         except requests.exceptions.RequestException as e:
    #             print(f"Error making API request: {e}")


    print("CSV file 'output.csv' has been created and populated with data.")




def get_station_distance(coordinates, input_file_path  =  "data/stations.csv"):
    """
    Extracts the distance of the train stations from the csv file
    Time spent cycling between each station
    """
    stations_dic = {}

    with open(input_file_path, "r") as input_file:
        next(input_file, None)
        for line in input_file:
            fields = line.strip().split(",")
            start = fields[0]
            end = fields[1]

            if start in coordinates  and end in coordinates:
                duration = float(fields[2])
                key = (start, end)
                stations_dic[key] = duration

    return stations_dic

def min_max_normalize(input_dict):
    min_value = min(input_dict.values())
    max_value = max(input_dict.values())
    normalized_dict = {key: (value - min_value) / (max_value - min_value) for key, value in input_dict.items()}
    return normalized_dict

# calculate the f and g for each station
# f is the annual ridership
# g is the distance from the nearest touristic site

def get_number_riders(file = 'data/Annual Total-Table 1.csv'):
    # Initialize an empty dictionary to store station sums
    station_rider_sums = {}

    # Open the CSV file for reading
    with open(file, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            # Extract station name and year data
            station_name = row[0]
            years_data = row[3:8]  # Extract years 2016 to 2020 (columns 4 to 8)

            # Remove commas and convert to integers
            years_data = [int(year.replace(',', '')) for year in years_data]

            # Calculate the sum for years 2016 to 2020
            sum_2016_to_2020 = sum(years_data)

            # Store the sum in the dictionary using station name as the key
            station_rider_sums[station_name] = sum_2016_to_2020
    
    return station_rider_sums

def clean(coordinates,station_rider_sums):
    # cleaning it
    modified_coordinates = {}
    modified_station_rider_sums = {}

    # Initialize a list to store missing keys
    missing_keys = []

    # Iterate through the keys in coordinates
    for key in coordinates.keys():
        matching_substring = None

        # Check if the key exists as a substring in the keys of station_rider_sums
        for s in station_rider_sums.keys():
            if key in s:
                matching_substring = key
                modified_station_rider_sums[matching_substring] = station_rider_sums[s]
                break  # Exit the loop if a matching substring is found

        if matching_substring:
            modified_coordinates[matching_substring] = coordinates[key]
        else:
            missing_keys.append(key)

    coordinates = modified_coordinates
    station_rider_sums = modified_station_rider_sums

    #normalize
    station_rider_sums = min_max_normalize(station_rider_sums)
    
    return coordinates, station_rider_sums


def get_distance_from_nearest_site(stations_dic):
    min_station_dist = {}

    for station1 in stations_dic.items():
        start = station1[0][0]
        min_dist = 1000

        # getting the distance to all the stations from 'start'
        for station2 in stations_dic.items():

            cur_start = station2[0][0]

            if start != cur_start:
                continue

            min_dist = min(min_dist, station2[1])

        # saving the minimum in teh dictionary
        min_station_dist[start] = min_dist

    return min_station_dist


