# Fetch shanghai stock data. Expect around 800-900 megabytes

import urllib2, csv

# http://real-chart.finance.yahoo.com/table.csv?s=601111.SS&a=07&b=18&c=1960&d=07&e=31&f=2015&g=d&ignore=.csv

# The stocks, from http://english.sse.com.cn/listed/list/
# Noticed that they run from 600000 to 603998 inclusive, then from
# 900901 to 900957 inclusive, skipping some numbers on the way
# in my experience, numbers that were skipped didn't appear on Yahoo Stocks
# so I just skip over them in this code if nothing appears, else
# assume that it's a shanghai stock
# If you really want data assurance I recommend adding under that optional
# section below, a quick bit of scraping Python code (BeautifulSoup) to check
# the stock id against the name and location on (http://finance.yahoo.com/q?s=600018.SS&ql=1)

# stocks = ["600000", "600004", "601111", "601113"] # just a hardcoded example
stocks = range(600000, 603998 + 1, 1) + range(900901, 900957 + 1, 1)
START_YEAR = 1950 # just so fetches earliest data
BASE_URL = "http://real-chart.finance.yahoo.com/table.csv?s="
URL_PARAMS = ".SS&a=07&b=18&c=%s&d=07&e=31&f=2015&g=d&ignore=.csv" % START_YEAR
# from aug 18 START_YEAR to aug 31 2015 (present). should cover everything
# params: see https://greenido.wordpress.com/2009/12/22/yahoo-finance-hidden-api/

for stock_id in stocks:
    print("Trying stock id %s ..." % stock_id)
    try:
        print("Stock for %s found!" % stock_id)
        # first download the data
        stock_url = "%s%s%s" % (BASE_URL, stock_id, URL_PARAMS)
        response = urllib2.urlopen(stock_url)
        csv = response.read()
        csvstr = str(csv).strip("b'")
        lines = csvstr.split("\\n")

        # Optional: lookup the stock name. Probably should cross check here
        # just to assure that it's actually a shanghai stock, but 
        # from looking at the company ids (http://english.sse.com.cn/listed/list/)
        # it looks like there aren't any other companies besides shanghai
        # stocks from the ranges [600000, 603998 + 1) and [900901, 900957 + 1]
        # stock_info = "%s%s&ql=1" % (BASE_URL, stock_id)

        # finally write to file
        f = open("historical_%s.csv" % stock_id, "w")
        for line in lines:
            f.write(line + "\n")
        f.close()
    except:
        print("Stock for %s not found" % stock_id)
        continue
