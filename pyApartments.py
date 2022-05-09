#%%
from sys import argv
import time
from src.items import ApartmentsPipeline
from src.db_postgres import dbPostgres

if __name__ == "__main__":
    # Collect the information to set up the scraping pipeline
    city_names = input("Enter the city name:  ").split(",")
    state_abbv = input("Enter the state abbreviation:  ")
    end_price = int(input("Enter the maximum price to consider for scraping URLs:  "))

    # Record the start time of the program
    start_time = time.time()

    # Scrape all of the cities
    for city in city_names:
        # Run the scraping pipeline
        print(f"Starting {city}")
        pipeline = ApartmentsPipeline(city, state_abbv, end_price=end_price)
        pipeline.run()
        print(f"Done with {city}")
        properties = pipeline.properties
        units = pipeline.units

        # Establish a connection to the database
        database = dbPostgres(
            dbname="apartments", user="postgres", password="postgres", port=5432
        )

        # Save all of the properties
        database.insert_properties(properties)

        # Save all of the units
        for prop_name, values in units.items():
            zipcode = values["zipcode"]
            units = values["units"]
            database.insert_units(units, prop_name, zipcode)

        # Close the connection
        database.close_connection()

    # Report the total time used
    print("Time used: {}".format(time.time() - start_time))


# %%
