#%%
from sys import argv
import numpy as np
import time
from src.scraper import make_request, generate_page_URL
import src.unit_parser as unit_parser
import src.property_parser as property_parser
import src.database as db
import pickle as pkl

db_file = "./data/apartments.db"


class ApartmentsPipeline:
    """A class for extracting raw HTML from Apartments.com, parsing, and saving to a db

    Methods:
        get_property_urls: Extracts the general information for each listing
        get_property_urls_details: Extract the listing details for each listing
    """

    def __init__(
        self,
        city_name: str,
        state_abbv: str,
        db_file: str,
        start_price: int = 500,
        end_price: int = 750,
        price_step: int = 250,
    ):
        """Constructs the attributes to use for web scraping apartments

        Args:
            city_name (str): City name to be scraped.
            state_abbv (str): Abbreviated state name to be scraped.
            db_file (str): Location of db for connection
            start_price (int, optional): Price to begin scraping. Defaults to 500.
            end_price (int, optional): Price to stop scraping. Defaults to 5000.
            price_step (int, optional): Sets the min and max price range. Defaults to 500.
        """

        self.start_price = int(start_price)
        self.end_price = int(end_price)
        self.price_step = int(price_step)
        self.city_name = city_name
        self.state_abbv = state_abbv
        self.conn = db.create_connection(db_file)
        self.BASE_URL = f"https://www.apartments.com/{city_name.lower().replace(' ', '-')}-{state_abbv.lower()}/"  # "/price range/page"
        self.price_range = list(np.arange(start_price, end_price, price_step))
        self.page_range = list(np.arange(1, 29, 1))
        self.property_urls = []
        self.empty_units_logger = []
        self.scrape_count = 0

        db.create_tables(self.conn)

    def sleep_crawler(self):

        if self.scrape_count > 0:
            if self.scrape_count % 100 == 0:
                time.sleep(round(np.random.uniform(15, 30)))

    def get_property_urls(self):

        # Loop through all price ranges
        for min_price in self.price_range:

            for page_num in self.page_range:
                self.sleep_crawler()
                url = generate_page_URL(
                    self.BASE_URL, min_price, min_price + self.price_step, page_num
                )
                soup, res_status = make_request(url)
                # If URL was redirected then end of page range was reached
                if res_status == 301:
                    break
                # If soup is None, skip iteration
                if soup == None:
                    continue

                listings = soup.find_all("li", {"class": "mortar-wrapper"})
                for listing in listings:
                    url = listing.find("a", {"class": "property-link"})["href"]
                    self.property_urls.append(url)
                # Add to the scraping counter
                self.scrape_count += 1

        # Remove any duplicate property URLs
        self.property_urls = list(set(self.property_urls))

    def scrape_property_urls(self):

        for url in self.property_urls:
            soup, res_status = make_request(url)
            # If soup is None, skip iteration
            if soup == None:
                continue
            try:
                property_name = soup.find("h1", {"class": "propertyName"}).get_text(
                    strip=True
                )
                # Extract all property details and save to the db
                property_data = self.save_property_data(
                    soup, property_name, self.city_name, url
                )
                # Find all of the current unit listings
                self.save_units_data(soup, property_name, property_data["zipcode"], url)

            except Exception as e:
                print(f"The exception, {e}, occured at the following URL: {url}")
                continue
            # Add to the scraping counter
            self.scrape_count += 1

        # Close db connection after all information is saved
        self.conn.close()

    def save_property_data(self, soup, property_name, city_name, url):
        property_data = property_parser.Property(
            property_name, url
        ).parse_property_page(soup)

        property_data["city_name"] = city_name
        db.insert_data(self.conn, property_data, "properties")

        return property_data

    def save_units_data(self, soup, property_name: str, zipcode: str, url: str):

        units = ApartmentsPipeline.get_all_units(soup)
        # Keep track of all units that don't have any units listed
        # This will alert me if the HTML format is likely different
        if len(units) == 0:
            self.empty_units_logger.append(url)

        # Get property_id
        property_id = db.get_property_id(self.conn, property_name, zipcode)

        # Extract each unit from the listing and save to the db
        for unit in units:
            current_unit = unit_parser.Single_Unit(property_id).parse_unit(unit)
            if current_unit["date_available"] != "Not Available":
                db.insert_data(self.conn, current_unit, "units")
            else:
                pass

    @staticmethod
    def get_all_units(soup):
        """Grab all units from a listing URl"""

        # Normal HTML layout for units
        units_html_1 = soup.find("div", {"data-tab-content-id": "all"}).find_all(
            "li", {"class": "unitContainer js-unitContainer"}
        )

        # Alternate HTML layout for units
        units_html_2 = soup.find("div", {"data-tab-content-id": "all"}).find_all(
            "div", {"class": "pricingGridItem multiFamily"},
        )
        units_html_3 = soup.find_all(
            "div", {"class": "priceGridModelWrapper js-unitContainer mortar-wrapper"},
        )
        if len(units_html_1) != 0:
            return units_html_1
        elif len(units_html_2) != 0:
            return units_html_2
        else:
            return units_html_3

    def run(self):
        print("Begin scraping...")
        self.get_property_urls()
        print("All property urls extracted")
        print(f"The total number of listings is {len(self.property_urls)}")
        self.scrape_property_urls()
        print("Done!")

        # Save the list of urls that had no units
        # with open("./data/no_units_found.pickle", "wb") as handle:
        #     pkl.dump(self.empty_units_logger, handle)


seattle_counties = ["King County"]

bay_area_counties = [
    "San Francisco",
    "Alameda County",
    "San Mateo County",
    "Santa Clara County",
]

nyc_counties = [
    "Manhattan County",
    "Bronx County",
    "Brooklyn",
    "Queens County",
    "Staten Island",
]

chicago_counties = ["Chicago"]

if __name__ == "__main__":

    # Collect the information to set up the scraping pipeline
    city_names = input("Enter the city name:  ").split(",")
    state_abbv = input("Enter the state abbreviation:  ")
    end_price = int(input("Enter the maximum price to consider for scraping URLs:  "))

    # Record the start time of the program
    start_time = time.time()

    # Scrape all of the cities
    for city in city_names:
        print(f"Starting {city}")
        pipeline = ApartmentsPipeline(city, state_abbv, db_file, end_price=end_price)
        pipeline.run()
        print(f"Done with {city}")

    # Report the total time used
    print("Time used: {}".format(time.time() - start_time))

# %%
