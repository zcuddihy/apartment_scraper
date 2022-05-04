import sqlite3
from sqlite3 import Error, IntegrityError


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

    query_property = """CREATE TABLE IF NOT EXISTS properties (
                        property_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_name NOT NULL,
                        city_name NOT NULL,
                        fitness_center INTEGER,
                        air_conditioning INTEGER,
                        in_unit_washer_dryer INTEGER,
                        dishwasher INTEGER,
                        laundry_facilities INTEGER,
                        car_charging INTEGER,
                        roof INTEGER,
                        concierge INTEGER,
                        pool INTEGER,
                        elevator INTEGER,
                        garage INTEGER,
                        dogs_allowed INTEGER,
                        cats_allowed INTEGER,
                        income_restrictions INTEGER,
                        latitude REAL,
                        longitude REAL,
                        neighborhood TEXT,
                        zipcode TEXT NOT NULL,
                        description TEXT,
                        unique_features TEXT,
                        property_url TEXT,
                        year_built INT,
                        UNIQUE(property_name, zipcode)
                        ); """

    query_apartments = """CREATE TABLE IF NOT EXISTS units (
                        unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unit_label TEXT,
                        rent INTEGER,
                        beds INTEGER,
                        baths REAL,
                        sqft REAL,
                        date_available TEXT,
                        date_scraped TEXT,
                        property_id INTEGER,
                        FOREIGN KEY(property_id) REFERENCES properties(property_id),
                        UNIQUE(property_id, unit_label, beds, baths, sqft, date_scraped)
                        ); """

    try:
        c = conn.cursor()
        c.execute(query_property)
        c.execute(query_apartments)
    except Error as e:
        print(e)


def insert_data(conn, data: dict, table_name: str):
    """Creates a SQL query to insert the dictionary data into the database"""
    try:
        c = conn.cursor()
        query = f"INSERT INTO {table_name} {str(tuple(data.keys()))} VALUES {str(tuple(data.values()))};"
        c.execute(query)
        conn.commit()
    except IntegrityError as e:
        pass


def update_data(conn, data: dict):
    """Creates a SQL query to update the property data in the database"""
    c = conn.cursor()
    query = f"""UPDATE properties 
                SET dishwasher="{data['dishwasher']}", year_built="{data['year_built']}", property_url="{data['property_url']}"
                WHERE property_name="{data['property_name']}"
                AND zipcode="{data['zipcode']}";"""
    c.execute(query)
    conn.commit()


def get_property_id(conn, property_name: str, zipcode: str):
    """Returns the property_id for the specified property"""
    c = conn.cursor()
    query = f"""SELECT p.property_id
                FROM properties p
                WHERE property_name="{property_name}"
                AND zipcode="{zipcode}";"""

    # fetchall returns a list containing a single tuple
    property_id = c.execute(query).fetchall()[0][0]
    return property_id

