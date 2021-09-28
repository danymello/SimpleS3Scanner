#Configuration of 3S

# name of buckets to whitelist
WHITELIST_BUCKETS = ['cloudtrail', 'templates', 'demo']


# retrieve ACL for each object (default = False) - Only retrive for each bucket
PER_OBJECT_ACL = False

#max results per API requests (default = 1000)
MAX_KEYS =  100

# in test mode, only request 1 page
TEST_MODE = True