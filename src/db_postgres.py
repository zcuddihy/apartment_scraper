import psycopg2
from psycopg2 import extras
from psycopg2.errors import UniqueViolation


class dbPostgres:
    def __init__(
        self, dbname: str, user: str, password: str, port: int, host: str = "localhost"
    ):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port
        self.host = host

        # Create a connection to the database
        self.conn = self.create_connection()

        # Create tables if they don't exist
        self.create_tables()

    def create_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                port=self.port,
            )
        except Exception as e:
            conn = None
            print(f"Unsuccessful connection, {e}")
        return conn

    def create_tables(self):
        """Creates the database tables if they do not exist"""

        query_property = """CREATE TABLE IF NOT EXISTS properties (
                            property_id SERIAL PRIMARY KEY,
                            property_name text NOT NULL,
                            city_name text NOT NULL,
                            fitness_center boolean,
                            air_conditioning boolean,
                            in_unit_washer_dryer boolean,
                            dishwasher boolean,
                            laundry_facilities boolean,
                            car_charging boolean,
                            roof boolean,
                            concierge boolean,
                            pool boolean,
                            elevator boolean,
                            garage boolean,
                            dogs_allowed boolean,
                            cats_allowed boolean,
                            income_restrictions boolean,
                            latitude real,
                            longitude real,
                            neighborhood text,
                            zipcode text NOT NULL,
                            description text,
                            unique_features text,
                            property_url text,
                            year_built int,
                            UNIQUE(property_name, zipcode)
                            ); """

        query_apartments = """CREATE TABLE IF NOT EXISTS units (
                            unit_id SERIAL PRIMARY KEY,
                            unit_label text,
                            rent int,
                            beds int,
                            baths real,
                            sqft real,
                            date_available date,
                            date_scraped date,
                            property_id int NOT NULL,
                            FOREIGN KEY(property_id) REFERENCES properties(property_id),
                            UNIQUE(property_id, unit_label, beds, baths, sqft, date_scraped)
                            ); """

        try:
            cur = self.conn.cursor()
            cur.execute(query_property)
            cur.execute(query_apartments)
            self.conn.commit()
            cur.close()
        except Exception as e:
            print(e)
            self.conn.rollback()

    def insert_properties(self, data: list):
        cur = self.conn.cursor()

        try:
            columns = data[0].keys()
            values = [
                tuple(value for value in prop_data.values()) for prop_data in data
            ]
            query = f"""INSERT INTO properties ({(', '.join(columns))}) 
                        VALUES %s
                        ON CONFLICT (property_id) DO NOTHING"""

            extras.execute_values(cur, query, values)
            self.conn.commit()
        except UniqueViolation:
            pass
        except Exception as e:
            print(e)
            self.conn.rollback()
        finally:
            cur.close()

    @staticmethod
    def get_property_id_query(property_name: str, zipcode: str):
        """Returns the query to get the property_id for the specified property"""
        query = f"""SELECT property_id
                    FROM properties
                    WHERE property_name = '{property_name}'
                    AND zipcode = '{zipcode}'
                    """
        return query

    def insert_units(self, data: dict, property_name: str, zipcode: str):
        cur = self.conn.cursor()

        try:
            columns = [
                "unit_label",
                "rent",
                "beds",
                "baths",
                "sqft",
                "date_available",
                "date_scraped",
            ]
            value_placeholders = ["%(" + item + ")s" for item in columns]
            property_id_query = self.get_property_id_query(property_name, zipcode)
            query = f"""INSERT INTO units (property_id, {(', '.join(columns))}) 
                        VALUES (({property_id_query}), {(', '.join(value_placeholders))})
                        ON CONFLICT (unit_id) DO NOTHING"""

            cur.executemany(query, data)
            self.conn.commit()
        except UniqueViolation:
            pass
        except Exception as e:
            print(f"Error: {e} at property: {property_name}")
            self.conn.rollback()
        finally:
            cur.close()

    def close_connection(self):
        self.conn.commit()
        self.conn.close()
