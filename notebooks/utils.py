import numpy as np
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
from sqlite3 import Error

# import googlemaps
import datetime
import re


def calculate_bearing(startLat, startLon, destLat, destLon):

    startLon, startLat, destLon, destLat = map(
        np.radians, [startLon, startLat, destLon, destLat]
    )

    dlon = destLon - startLon
    x = np.cos(destLat) * np.sin(dlon)
    y = np.cos(startLat) * np.sin(destLat) - np.sin(startLat) * np.cos(
        destLat
    ) * np.cos(dlon)

    brng = np.arctan2(x, y)
    return (np.degrees(brng) + 360) % 360


def calculate_distance(startLat, startLon, destLat, destLon):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    startLon, startLat, destLon, destLat = map(
        np.radians, [startLon, startLat, destLon, destLat]
    )

    dlon = destLon - startLon
    dlat = destLat - startLat

    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(startLat) * np.cos(destLat) * np.sin(dlon / 2.0) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    miles = 3958.756 * c
    return miles


def make_request(
    url: str,
    min_sleep: int = 1,
    max_sleep: int = 7,
    timeout: int = 10,
    retry_attempt: bool = False,
):
    """Web scraper for a given URL with request rate control built in

        Args:
            url (str): URL to request
            min_sleep (int, optional): Minimum time to sleep for request rate 
                                    control.
            max_sleep (int, optional): Max time to sleep for request rate control
            timeout (int, optional): Max timeout setting for request
            retry_attempt (bool, optional): True/False variable to check if this is a retry after a timeout error

        Returns:
            BeautifulSoup: Raw HTML from request module. None is returned if status code is not 200.
            res.status_code: Status code from request to check if request was successful.
        """

    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    ]

    # Control the request rate
    time.sleep(round(np.random.uniform(min_sleep, max_sleep)))

    # Pick a random user agent and set headers
    user_agent = np.random.choice(user_agents)
    headers = {"User-Agent": user_agent}

    # Try/except block to execute the request and handle any exceptions
    try:
        res = requests.get(url, allow_redirects=False, headers=headers, timeout=timeout)
        # If the response was successful, no Exception will be raised
        res.raise_for_status()
    except requests.exceptions.Timeout:
        print("Timeout error occurred")

        # Try request again after a delay
        # If retry attempt is true, need to exit method
        if retry_attempt == False:
            time.sleep(round(np.random.uniform(10, 20)))
            make_request(url, retry_attempt=True)
        else:
            soup = None
            status_code = 404
            return soup, status_code
    except Exception as e:
        print(f"An error occured, {e}, while trying to access the URL: {url}")
        soup = None
        status_code = 404
        return soup, status_code

    # Verify that the request was successful
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "lxml")
    elif res.status_code == 403:
        print("403 Error, IP banned")
        soup = None
    else:
        soup = None

    return soup, res.status_code


def find_string_index(list_of_strings, substring):
    """Returns the index in a list if the substring is in the string from the list"""
    try:
        return next(
            stringIndex
            for stringIndex, string in enumerate(list_of_strings)
            if substring in string
        )
    except:
        return None


def generate_page_URL(base_url: str, min_price: int, max_price: int, page_num: int):
    """Generates a page URL with the current price range and page number"""
    return base_url + f"{min_price}-to-{max_price}/{page_num}/"


def create_connection(database):
    """ Creates a connection to the specified database"""

    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)

    return conn


# def google_distance_matrix(
#     origin_lat, origin_lng, destination_lat, destination_lng, mode
# ) -> int:

#     # Control the request rate
#     time.sleep(1)

#     # Defaults for the request
#     API_KEY = "AIzaSyAzCVQrg9R2aGgW9yKCz5t06xWrz9E6Gyg"
#     units = "imperial"

#     # Converting the lat/long pairs
#     origins = (origin_lat, origin_lng)
#     destinations = (destination_lat, destination_lng)

#     # Create a departure_time of 8:00AM on the next Monday
#     today = datetime.date.today()
#     next_monday = today + datetime.timedelta(days=-today.weekday(), weeks=1)
#     next_monday = datetime.datetime(
#         next_monday.year, next_monday.month, next_monday.day, 8, 0, 0
#     )

#     # Connect to the Google Maps API
#     gmaps = googlemaps.Client(key=API_KEY)
#     result = gmaps.distance_matrix(
#         origins=origins,
#         destinations=destinations,
#         units=units,
#         mode=mode,
#         departure_time=next_monday,
#     )

#     # Get duration of trip from result JSON
#     commute_time = result["rows"][0]["elements"][0]["duration"]["text"]
#     commute_time = int(re.sub("[^\d\.]", "", commute_time))

#     return commute_time
