from math import radians, sin, cos, acos

import pandas as pd


class City:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = radians(latitude)
        self.longitude = radians(longitude)


class Flight:
    def __init__(self, source, destination, departure, arrival, flight_number, days):
        self.source = source
        self.destination = destination
        self.departure = departure
        self.arrival = arrival
        self.flight_number = flight_number
        self.days = days


class Route:
    def __init__(self, total_cost, flights):
        self.total_cost = total_cost
        self.flights = flights


data_file = pd.ExcelFile(r'Tarvelagent.xlsx')

data_cities = pd.read_excel(data_file, 'Cities')
data_flights = pd.read_excel(data_file, 'Flights')


def convert_data_frame_to_city():
    cities_list = []
    for index, row in data_cities.iterrows():
        cities_list.append(City(row['City'], row['Latitude'], row['Longitude']))
    return cities_list


def convert_data_frame_to_flight():
    flights_list = []
    for index, row in data_flights.iterrows():
        flights_list.append(
            Flight(row['Source'], row['Destination'], row['Departure Time'], row['Arrival Time'], row['Flight Number'],
                   convert_string_to_list(row['List of Days'])))

    return flights_list


def convert_string_to_list(s):
    s_substring = ""
    if s[0] == "[" and s[-1] == "]":
        s_substring = s[1:-1]
        # print(s_substring)
    my_list = []
    for day in s_substring.split(","):
        my_list.append(day.strip())
    return my_list


def get_distance(source, destination):
    if source is None:
        return 0
    if destination is None:
        return 0
    return 6371.01 * acos(
        sin(source.latitude) * sin(destination.latitude) + cos(source.latitude) * cos(destination.latitude) * cos(
            source.longitude - destination.longitude))


def check_flight_days(days_query, day_list):
    if days_query in day_list:
        return True
    return False


def find_city_by_name(city_name):
    for city_ in cities:
        if city_.name.strip() == city_name.strip():
            return city_
    return None


def get_city_flights(city, day_range):
    city_flights = []
    for flight in flights:
        if flight.source == city and check_flight_days(day_range, flight.days):
            city_flights.append(flight)
    return city_flights


cities = convert_data_frame_to_city()
flights = convert_data_frame_to_flight()
expansions = []
routes = []


def expand(city_name, day_range):
    for city in expansions:
        if city_name == city:
            return []
    expansions.append(city_name)
    return get_city_flights(city_name, day_range)


def search(route, final_destination, day_range):
    last_flight = route.flights[-1]  # -1 get last element of the list
    city_flights = expand(last_flight.destination, day_range)
    if last_flight.destination == final_destination:
        routes.append(route)
        return
    if len(city_flights) == 0:
        return
    best_flight = get_nearest_city(city_flights)
    route.flights.append(best_flight)
    route.total_cost = route.total_cost + get_distance(find_city_by_name(best_flight.source),
                                                       find_city_by_name(best_flight.destination))
    search(route, final_destination, day_range)


def get_nearest_city(city_flights):
    best_flight = city_flights[0]
    min_distance = get_distance(find_city_by_name(best_flight.source), find_city_by_name(best_flight.destination))
    for flight in city_flights:
        temp = get_distance(find_city_by_name(flight.source), find_city_by_name(flight.destination))
        if check_destination(city_flights, flight):
            if temp < min_distance:
                best_flight = flight
    return best_flight


def check_destination(_flights, flight):
    found = False
    for route in _flights:
        if (route.source == flight.source and route.destination == flight.destination) or (
                route.source == flight.destination):
            found = True
    return found


def get_best_route():
    if len(routes) == 0:
        print("No available routes")
        return
    best_route = routes[0]
    for r in routes:
        if best_route.total_cost > r.total_cost:
            best_route = r
    for f in best_route.flights:
        index = best_route.flights.index(f) + 1
        print("Step " + str(index) + " " + f.flight_number + " Travel from " + f.source + ' To ' + f.destination,
              "Departure Time " + str(f.departure), "Arrival Time",
              str(f.arrival))


def start(source, destination, day_range):
    historical_cost = get_distance(find_city_by_name(source), find_city_by_name(destination))
    ways = get_city_flights(source, day_range)
    for w in ways:
        initial_route = Route(
            get_distance(find_city_by_name(w.source), find_city_by_name(w.destination)) + historical_cost,
            [w])
        search(initial_route, destination, day_range)
    get_best_route()


start("Cairo", "San Francisco", "mon")
