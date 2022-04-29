# Apartments.com Scraper

This tool scrapes all listing on apartments.com given a specific city name and loads the data into a SQLite database. The general process of the web scraping is the following:

* Accept input from the user on which city to scrape. Additionally, a minimum and maximum rent range can be specified. If no range is provided it defaults to min =  $500 and max = $6,000
* Crawl through all pages for the given rent range in incrememnts of $250 to captrue all possible listings. All apartment listings from each page are stored in a list.
* Run a for loop over the list to crawl through each apartment listing and store the data.
* Load the crawled data into a SQLite database. The data is split into two tables: units and properties (more on this further down).
