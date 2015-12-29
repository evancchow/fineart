# Scrape data from Blouin's art index
# cd Desktop/Fall 2015/thesis/data_fineart/blouin_spider/
# Focus on top artists only:
# http://artsalesindex.artinfo.com.ezproxy.princeton.edu/asi/top_artist.jsp
# 

# Step 1: enter "Pablo Picasso" in the form, also only for prints. download results
# page.
# Note, you should sign into Princeton VPN before running script otherwise have
# to deal with Princeton authentication.
# http://artsalesindex.artinfo.com.ezproxy.princeton.edu/asi/search.action

import scrapy

class BlouinSpider(scrapy.Spider):
    name = "blouin"
    allowed_domains = ["artsalesindex.artinfo.com.ezproxy.princeton.edu"]
    start_urls = [
        "http://artsalesindex.artinfo.com.ezproxy.princeton.edu/asi/search.action"
    ]

    def parse(self, response):
        filename = response.url.split("/")[-2] + ".html"
        with open(filename, 'wb') as f:
            f.write(response.body)
