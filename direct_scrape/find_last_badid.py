# Find last badid

import itertools

LOWER = 6102186
UPPER = 6500005

badids_filename = "blouin_badids_{}_to_{}.csv".format(LOWER, UPPER)
bad_ids = [int(line) for line in reversed(open(badids_filename).readlines())]

# cycle backward
should_have_ids = range(bad_ids[0], 5940000, -1)
# import code; code.interact(local=locals())
num_bad_at_end = 0
for bi, shi in itertools.izip(bad_ids, should_have_ids):
    print "bad_id, should_id:   {}   {}".format(bi, shi)
    if bi != shi:
        print "Start of bad ids found! ^^ (last bad_id - 1) = last good id"
        break
    num_bad_at_end += 1

print "Total number of bad ids: ", len(bad_ids)
print "Total number of REAL bad ids before started losing internet connection: {}".format(len(bad_ids) - num_bad_at_end)
# all approximate