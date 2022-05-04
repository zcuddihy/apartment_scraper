#%%
from dataclasses import dataclass, field
import re


@dataclass
class Property:
    property_name: str
    property_url: str
    description: str = field(init=False)
    amenities: dict = field(default_factory=dict)
    unique_features: list = field(default_factory=list)
    location: dict = field(default_factory=dict)
    year_built: str = field(init=False)

    def get_property_description(self, soup):
        raw_description = soup.find("section", {"id": "descriptionSection"}).find_all(
            "p"
        )
        # Extract all of the paragraphs
        paragraphs = []
        for paragraph in raw_description:
            paragraphs.append(paragraph.get_text(strip=True))

        raw_description = " ".join(paragraphs).replace("\n", "")
        raw_description = re.sub("[']", "", raw_description)
        raw_description = re.sub("[:]", "", raw_description)
        self.description = re.sub('"', "", raw_description)

    def extract_amenities(self, soup):
        """Parse the property HTML and search for various amenities"""

        # amenities to check for on the url
        # Key = the html element feature name
        # Value = the html element the value should be stored in
        html_amenities = {
            "Fitness Center": "span",
            "Air Conditioning": "span",
            "In Unit Washer & Dryer": "span",
            "Dishwasher": "span",
            "Laundry Facilities": "span",
            "Car Charging": "span",
            "Roof": "span",
            "Concierge": "span",
            "Pool": "span",
            "Elevator": "span",
            "Garage": "div",
            "Dogs Allowed": "h4",
            "Cats Allowed": "h4",
            "Income Restrictions": "h2",
        }
        for amenity, html_element in html_amenities.items():
            amenity_check = (
                False
                if soup.find(html_element, text=re.compile(amenity)) == None
                else True
            )
            # The amenity name has to match the HTML lookup,
            # however, it needs to be converted to a proper format
            # for the database.
            cleaned_amenity_name = amenity.lower().replace(" & ", " ").replace(" ", "_")
            self.amenities[cleaned_amenity_name] = amenity_check

    def extract_unique_features(self, soup):
        """Parse the property HTML and collect a list of the unique features"""
        try:
            unique_features = soup.find("div", {"id": "uniqueFeatures"}).find_all(
                "li", {"class": "specInfo uniqueAmenity"}
            )
            # Extract the text of all the features
            for feature in unique_features:
                cleaned_feature = re.sub("[']", "", feature.get_text(strip=True))
                cleaned_feature = re.sub('"', "", cleaned_feature)
                self.unique_features.append(cleaned_feature)
        # Some listings don't have any unique features listed
        # find_all() will throw an error in this case
        except:
            pass

    def extract_location(self, soup):
        """Parse the property HTML and search for location amenities"""

        try:
            latitude = soup.find("meta", {"property": "place:location:latitude"})[
                "content"
            ]
            longitude = soup.find("meta", {"property": "place:location:longitude"})[
                "content"
            ]
        except:
            latitude = None
            longitude = None

        try:
            neighborhood = soup.find("a", {"class": "neighborhood"}).get_text(
                strip=True
            )
            zipcode = re.sub(
                "[\D]",
                "",
                soup.find("span", {"class": "stateZipContainer"}).get_text(strip=True),
            )
        except:
            neighborhood = None
            zipcode = None

        self.location["latitude"] = latitude
        self.location["longitude"] = longitude
        self.location["neighborhood"] = neighborhood
        self.location["zipcode"] = zipcode

    def get_year_built(self, soup):
        try:
            year_built = soup.find("div", text=re.compile("Built in")).get_text(
                strip=True
            )
            self.year_built = re.sub("[\D]", "", year_built)
        except:
            self.year_built = None

    def parse_property_page(self, soup):
        self.get_property_description(soup)
        self.extract_amenities(soup)
        self.extract_unique_features(soup)
        self.extract_location(soup)
        self.get_year_built(soup)

        # Combined all of the dictionaries and other property values
        combined = (
            {"property_name": self.property_name} | self.amenities | self.location
        )
        combined["description"] = str(self.description)

        if len(self.unique_features) != None:
            combined["unique_features"] = ", ".join(self.unique_features)
        else:
            pass

        if self.year_built != None:
            combined["year_built"] = self.year_built

        combined["property_url"] = str(self.property_url)
        return combined

