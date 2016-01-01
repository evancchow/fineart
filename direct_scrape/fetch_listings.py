######################################################################
#
# Scrape data from Blouin etc.
# Remember to use Princeton's VPN!
# Make sure you connect BEFORE you use your browser. If you try to connect
# while you are already logged in it won't work.
# If have problems, right-click VPN then hit "clear saved login info" or 
# whatever it says.
# + Auto refresh for Chrome on both Blouin, Blackboard so don't get logged out
#
######################################################################

from bs4 import BeautifulSoup
import urllib2, re, time, unicodedata, sys, linecache
import pdb

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


EXIT_PROGRAM = False

BASE_URL = "http://artsalesindex.artinfo.com.ezproxy.princeton.edu/asi/lots/" # in future version, might be able to leave out the ezproxy.princeton.edu

# just for Picasso for now
LOWER = 5800000
UPPER = 5950000
painting_ids = xrange(LOWER, UPPER + 1)

# CSV file to have the data
fd = open("./blouin_data_{}_to_{}.csv".format(LOWER, UPPER), 'wb')
# CSV file to have the good fileids
good_fileids = open("./blouin_goodids_{}_to_{}.csv".format(LOWER, UPPER), 'wb')
# CSV file to have the bad fileids
bad_fileids = open("./blouin_badids_{}_to_{}.csv".format(LOWER, UPPER), 'wb')

##########################################################################

num_ids_remaining = UPPER - 1 - LOWER
num_ids_printed = 1
num_ids_invalid = 0 # previously started at 1 so may have off-by-one errors in previous versions
num_picassos = 0

## For tracking time remaining w/recursively updated average
## DO LATER if time
PREV_TIME = time.time()
# MU = time.time() - PREV_TIME # starts around 0
# N = 1

for cx, curr_id in enumerate(painting_ids):
    if num_ids_remaining >= 0:
        # Information: which painting you're on, how much time remaining (estimate).
        # Multiple average time so far by number of paintings left.
        print "-----> Painting {} (# {} so far), going from {} to {} ...".format(curr_id, curr_id - LOWER, LOWER, UPPER)
        print "    Paintings remaining: {}".format(num_ids_remaining)
        print "    Printed, invalid so far: {}, {}".format(num_ids_printed, num_ids_invalid)
        CURR_TIME = time.time()
        REMAINING_TIME = num_ids_remaining * (CURR_TIME - PREV_TIME)
        # based only on last interval
        m_remain, s_remain = divmod(REMAINING_TIME, 60)
        h_remain, m_remain = divmod(m_remain, 60)
        print "    Estimated h/m/s remaining: %d:%02d:%02d" % (h_remain, m_remain, s_remain)
        PREV_TIME = CURR_TIME
        num_ids_remaining -= 1

    ######################
    # pdb.set_trace()
    ######################

    try:
        curr_url = "{}{}".format(BASE_URL, curr_id)
        response = urllib2.urlopen(curr_url)
        html = response.read()
        if len(html) < 10: # if empty HTML page
            print("        ERROR: empty html page")
            continue
        bs = BeautifulSoup(html, "lxml")
        """ STOP IF YOU GET LOGGED OUT OF PRINCETON VPN """
        print "   Page title: {}".format(bs.html.head.title)
        extracted_title = unicodedata.normalize("NFKD",
            bs.html.head.title.get_text()).encode("ascii", "ignore")
        print extracted_title
        if "Authentication Service" in extracted_title:
            EXIT_PROGRAM = True
            print("ENCOUNTERED PU LOGIN at url {}, going from {} to {}".format(curr_url, LOWER, UPPER))
            raise Exception()

        painting_info = bs.find("div", {"id" : "lotcontainer"})
        # get artist
        artist = painting_info.find("input", {"id" : "artistName"})["value"]

        ### Only if interested in Picasso
        # if "Picasso" not in artist:
            # continue
        if "Picasso" in artist:
            print "  Found a Picasso!"
            num_picassos += 1
            print "  Picassos seen so far: {}".format(num_picassos)

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
        formatted_data = [str(curr_id)]

        ####################
        # pdb.set_trace()
        ####################

        for item in data:
            if not item:
                formatted_data.append("")
                continue
            if isinstance(item, unicode):
                new_item = unicodedata.normalize('NFKD', item).encode('ascii', 'ignore').lstrip().rstrip()
            elif isinstance(item, str):
                new_item = item.lstrip().rstrip()
            elif isinstance(item, list):
                new_item = []
                for i in item:
                    if isinstance(i, unicode):
                        i = unicodedata.normalize('NFKD', i).encode('ascii', 'ignore')
                    new_item.append(i.lstrip().rstrip().replace("\n", " "))
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
        print "  Printing ..."
        fd.write(csv_line + "\n")
        print "  Painting {} printed: {} by {}".format(num_ids_printed,
            formatted_data[2], formatted_data[0])
        good_fileids.write("{}\n".format(curr_id))
        if cx % 1 == 0:
            fd.flush()
            good_fileids.flush()
            print "  FLUSH OUTPUT"
        num_ids_printed += 1

    #### if doesn't work just continue, collecting data is more important.
    except:
        PrintException()
        # "Nonetype has no attribute" -> okay, just means redirected to landing page

        if EXIT_PROGRAM == True:
            print "PROGRAM STOPPED BECAUSE LOGGED OUT OF PRINCETON VPN"
            import code; code.interact(local=locals())

        print " Painting {} had invalid data, writing to file".format(curr_id)
        bad_fileids.write("{}\n".format(curr_id))
        bad_fileids.flush()
        print " # paintings invalid so far: {}".format(num_ids_invalid)
        num_ids_invalid += 1

fd.close()
good_fileids.close()
bad_fileids.close()
print "Finished job."
print "----- SUMMARY -----"
print "Total number of paintings: {}".format(UPPER - 1 - LOWER)
print "Number of paintings printed: {}".format(num_ids_printed)
print "Number of paintings invalid: {}".format(num_ids_invalid)
print "Number of Picassos: {}".format(num_picassos)

import code; code.interact(local=locals())