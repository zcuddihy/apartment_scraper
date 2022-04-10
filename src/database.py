import sqlite3
from sqlite3 import Error


def create_connection(database):
    """Creates a connection to the specified database"""

    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    """Creates the database tables if they do not exist"""

    query_apartments = """CREATE TABLE IF NOT EXISTS units (
                        property_name,
                        property_zipcode,
                        unit_id,
                        rent,
                        beds,
                        baths,
                        sqft,
                        date_available,
                        date_scraped
                        ); """

    query_property = """CREATE TABLE IF NOT EXISTS properties (
                        property_name,
                        fitness_center,
                        air_conditioning,
                        in_unit_washer_dryer,
                        dishwasher,
                        laundry_facilities,
                        car_charging,
                        roof,
                        concierge,
                        pool,
                        elevator,
                        garage,
                        dogs_allowed,
                        cats_allowed,
                        income_restrictions,
                        latitude,
                        longitude,
                        neighborhood,
                        zipcode,
                        description,
                        unique_features,
                        city_name,
                        property_url,
                        year_built
                        ); """
    try:
        c = conn.cursor()
        c.execute(query_apartments)
        c.execute(query_property)
    except Error as e:
        print(e)


def insert_data(conn, data: dict, table_name: str):
    """Creates a SQL query to insert the dictionary data into the database"""
    c = conn.cursor()
    query = f"INSERT INTO {table_name} {str(tuple(data.keys()))} VALUES {str(tuple(data.values()))};"
    c.execute(query)
    conn.commit()


def update_data(conn, data: dict):
    """Creates a SQL query to update the property data in the database"""
    c = conn.cursor()
    query = f"""UPDATE properties 
                SET dishwasher="{data['dishwasher']}", year_built="{data['year_built']}", property_url="{data['property_url']}"
                WHERE property_name="{data['property_name']}"
                AND zipcode="{data['zipcode']}";"""
    c.execute(query)
    conn.commit()


def property_exists(conn, property_name: str, zipcode: str):
    """Checks if the property already exists in the database"""
    c = conn.cursor()
    query = f"""SELECT EXISTS(SELECT 1 
                FROM properties 
                WHERE property_name="{property_name}"
                AND zipcode="{zipcode}"
                LIMIT 1);"""

    # fetchall returns a list containing a single tuple
    return c.execute(query).fetchall()[0][0]

