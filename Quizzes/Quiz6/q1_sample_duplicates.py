#!/usr/bin/env python3


# Determine the average number of duplicate queries issued by a given user
import sys
import hashlib

# Read this many total lines, length of a "day"
read_num_lines = 240

# Read first a buckets
a = 1
# Number of total buckets
b = 2
# Sampling an a/b fraction of all read in results, discarding others

num_progress_updates = 10
i = 0
query_log = {}
while read_num_lines > i:
    linelist = sys.stdin.readline().strip().split()
    user, query = linelist[4], linelist[6]
    hash_object = hashlib.sha1()
    hash_object.update(user.encode('utf-8'))
    hash_int = int(hash_object.hexdigest(), 16)
    if hash_int % b < a:
        # If falls in first a buckets, record data
        if user not in query_log:
            query_log[user] = [query]
        else:
            query_log[user].append(query)
    # Otherwise, discard data
    i += 1
    if i % (read_num_lines/num_progress_updates) == 0:
        print(f'Sampling line {i} of {read_num_lines}')

duplicates_each = []
for user in query_log:
    num_duplicates = len(query_log[user]) - len(set(query_log[user]))
    duplicates_each.append(num_duplicates)
print(f'Average number of duplicates: {sum(duplicates_each)/len(duplicates_each)}')
