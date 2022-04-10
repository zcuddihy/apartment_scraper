#%%

import formatting
import numpy as np


def test_format_rent():
    rent = "$1,250"
    assert formatting.format_rent(rent) == 1250

    rent = None
    assert formatting.format_rent(rent) == None

    rent = "$1,250–$1,300"
    assert formatting.format_rent(rent) == 1275

    rent = "Call for Rent"
    assert formatting.format_rent(rent) == ""

    print("No issues with format_rent")


def test_format_beds():
    beds = "Studio"
    assert formatting.format_beds(beds) == "0"

    beds = None
    assert formatting.format_beds(beds) == None

    beds = "1 bed"
    assert formatting.format_beds(beds) == "1"

    beds = "5"
    assert formatting.format_beds(beds) == "5"

    print("No issues with format_beds")


def test_format_baths():
    baths = "1 baths"
    assert formatting.format_baths(baths) == "1"

    baths = None
    assert formatting.format_baths(baths) == None

    baths = "0.5 baths"
    assert formatting.format_baths(baths) == "0.5"

    baths = "5"
    assert formatting.format_baths(baths) == "5"

    print("No issues with format_baths")


def test_format_sqft():
    sqft = "100 sq ft"
    assert formatting.format_sqft(sqft) == "100"

    sqft = "1,200 sq ft"
    assert formatting.format_sqft(sqft) == "1200"

    sqft = None
    assert formatting.format_sqft(sqft) == None

    print("No issues with format_baths")


def test_format_date():
    date = "Now"
    assert formatting.format_date_available(date) == "2022-03-30"

    date = "Soon"
    assert formatting.format_date_available(date) == "2022-03-30"

    date = "Apr 16"
    assert formatting.format_date_available(date) == "2022-04-16"

    date = "Apr. 16"
    assert formatting.format_date_available(date) == "2022-04-16"

    date = "Not Available"
    assert formatting.format_date_available(date) == "Not Available"

    print("No issues with format_date")


test_format_rent()
test_format_beds()
test_format_baths()
test_format_sqft()
test_format_date()

