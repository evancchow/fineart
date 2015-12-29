######################################################################
#
# Scrape data from Blouin etc.
# Remember to use Princeton's VPN!
#
######################################################################

import os; clear = lambda: os.system("cls")
from bs4 import BeautifulSoup
import urllib2, re

BASE_URL = "http://artsalesindex.artinfo.com.ezproxy.princeton.edu/asi/lots/"

# just for Picasso for now
# ids 5941080 to 6089000
# painting_ids = [5943686, 5977558, 5960084, 5957888]
LOWER = 5900000
UPPER = 5900010
# UPPER = 6010000
painting_ids = xrange(LOWER, UPPER + 1)

# CSV file to have the data
fd = open("./blouin_data_{}_to_{}.csv".format(LOWER, UPPER), 'wb')
# CSV file to have the bad fileids
bad_fileids = open("./blouin_badids_{}_to_{}.csv".format(LOWER, UPPER), 'wb')

##########################################################################

for curr_id in painting_ids:
    print "Painting {}, going from {} to {} ...".format(curr_id, LOWER, UPPER)
    try:
        curr_url = "{}{}".format(BASE_URL, curr_id)
        response = urllib2.urlopen(curr_url)
        html = response.read()
        if len(html) < 10: # if empty HTML page
            continue
        bs = BeautifulSoup(html, "lxml")
        painting_info = bs.find("div", {"id" : "lotcontainer"})
        # get artist
        artist = painting_info.find("input", {"id" : "artistName"})["value"]

        ### Only if interested in Picasso
        # if "Picasso" not in artist:
        #     continue

        # get artist DOB
        artist_dob = painting_info.find("p", {"id" : "artistDob"}).get_text()
        # title of painting
        title = painting_info.find("h4", {"class" : "title"}).get_text()
        # lot num
        lot_number = painting_info.find("h2", {"class" : "lotnumber"}).get_text()
        # auction data (e.g. fine art and antiques category)
        auction_data = painting_info.find("p", {"class" : "auctiondata"}).get_text()
        # get various prices (which are in HTML multiple lines so use regex to remove weird chars).
        # THIS ALSO MENTIONS IF THE ITEM WAS BOUGHT IN.
        prices = re.sub(r'[^\x00-\x7F]+','\t', painting_info.find("div", {"class" : "price"}).get_text()).split('\t')
        # lot details: original currency of sale, estimate of price, etc.
        lot_details = [i.get_text() for i in painting_info.findAll("div", {"class" : "lot-details1"}) if len(i) > 1]
        # hedonic details
        painting_details = [i.get_text() for i in painting_info.findAll("p", {"class" : "artworkdetails"}) if len(i) > 1]

        ##### FORMAT DATA #####
        data_names = ["Artist", "Artist DOB", "Title", "Lot #", "Auction data", "Prices",
            "Lot details", "Painting details"]
        data = [artist, artist_dob, title, lot_number, auction_data, prices, lot_details, painting_details]
        formatted_data = []
        for item in data:
            if not item:
                formatted_data.append("")
                continue
            if isinstance(item, unicode):
                new_item = str(item).lstrip().rstrip()
            elif isinstance(item, str):
                new_item = str(item).lstrip().rstrip()
            elif isinstance(item, list):
                new_item = []
                for i in item:
                    if not isinstance(i, str) or not isinstance(i, unicode):
                        i = re.sub(r'[^\x00-\x7F]+',' ', i)
                    i = str(i).lstrip().rstrip().replace("\n", " ")
                    new_item.append(i)
            else:
                print "\n\nNot a list, string, or unicode! None data accounted for."
                print item
                print type(item)
                # raise Exception("This item is not valid!")
                formatted_data.append("")
                continue # just leave the data field empty
            formatted_data.append(new_item)

        # ##### PRINT OUT FORMATTED DATA #####
        # print "----- SCRAPED DATA | Painting {} -----".format(curr_id)
        # for d_name, d_data in zip(data_names, formatted_data):
        #         print "{}: ".format(d_name)
        #         print "    {}".format(d_data)
        # print

        ##### JOIN DATA TO WRITE TO CSV FILE #####
        # csv_data = []
        # for item in formatted_data:
        #     if not isinstance(item, list):
        #         csv_data.append(item)
        #     else: # append list as single string
        #         csv_data.append(' '.join(item))
        # csv_line = '|||||'.join(csv_data) # separator is |||||
        csv_line = '|||||'.join([item if not isinstance(item, list)
            else ' '.join(item) for item in formatted_data])
        fd.write(csv_line + "\n")

    #### if doesn't work just continue, collecting data is more important.
    except:
        print "Painting {} had invalid data, writing to file"
        bad_fileids.write(curr_id + "\n")

fd.close()
bad_fileids.close()
print "Finished job"

import code; code.interact(local=locals())