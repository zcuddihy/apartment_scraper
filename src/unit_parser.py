#%%
from dataclasses import dataclass, field
from .formatting import clean_unit_information
from datetime import date


@dataclass
class Unit_Parser:
    unit_label: str = field(init=False)
    rent: str = field(init=False)
    beds: str = field(init=False)
    baths: str = field(init=False)
    area: str = field(init=False)
    date_available: str = field(init=False)

    def get_unit_label(self, unit):
        try:
            self.unit_label = unit["data-unit"]
        except:
            self.unit_label = unit.find("span", {"class": "modelName"}).text

    def get_rent(self, unit):
        try:
            self.rent = (
                unit.find("div", {"class": "pricingColumn column"})
                .find_next()
                .find_next()
                .get_text(strip=True)
            )
        except:
            self.rent = unit.find("span", {"class": "rentLabel"}).text

    def get_bedrooms(self, unit):
        try:
            self.beds = unit["data-beds"]
        except:
            self.beds = (
                unit.find("span", {"class": "detailsTextWrapper"})
                .find_all("span")[0]
                .get_text()
            )

    def get_bathrooms(self, unit):
        try:
            self.baths = unit["data-beds"]
        except:
            self.baths = (
                unit.find("span", {"class": "detailsTextWrapper"})
                .find_all("span")[1]
                .get_text()
            )

    def get_sqft(self, unit):
        try:
            self.area = (
                unit.find("div", {"class": "sqftColumn column"})
                .get_text(strip=True)
                .strip("square feet")
            )
        except:
            self.area = (
                unit.find("span", {"class": "detailsTextWrapper"})
                .find_all("span")[2]
                .get_text()
            )

    def get_date_available(self, unit):
        try:
            self.date_available = (
                unit.find("span", {"class": "dateAvailable"})
                .get_text(strip=True)
                .strip("availability")
            )
        except AttributeError:
            self.date_available = unit.find(
                "span", {"class": "availabilityInfo"}
            ).get_text()
        except:
            self.date_available = None

    @clean_unit_information
    def parse_unit(self, unit):
        self.get_unit_label(unit)
        self.get_rent(unit)
        self.get_bedrooms(unit)
        self.get_bathrooms(unit)
        self.get_sqft(unit)
        self.get_date_available(unit)

        return {
            "unit_label": self.unit_label,
            "rent": self.rent,
            "beds": self.beds,
            "baths": self.baths,
            "sqft": self.area,
            "date_available": self.date_available,
            "date_scraped": date.today().strftime("%Y-%m-%d"),
        }

