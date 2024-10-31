#!/usr/bin/env python3

import sys
import hashlib
import matplotlib.pyplot as plt


def estimate_unique_users(bucket_maxes, m):
    return m*(2**(sum(bucket_maxes.values())/m))

# Read this many total lines
read_num_lines = 10000
num_graph_samples = 50

# Number of bits that are used to represent the bucket id
bucket_id_bits = 4
# Total number of possible buckets
m = 2**bucket_id_bits

bucket_maxes = {}
max_leading_zeros = 0

i = 0
user_estimates = []
user_estimates_x = []
while read_num_lines > i:
    linelist = sys.stdin.readline().strip().split()
    user = linelist[4]
    hash_object = hashlib.sha1()
    hash_object.update(user.encode('utf-8'))
    # Convert to 64 bit binary string
    bin_64 = bin(int.from_bytes(hash_object.digest(), 'little'))[-64:]
    bucket_id, remaining_bits = bin_64[:bucket_id_bits], bin_64[bucket_id_bits:]
    # Add 1 to end for all zeros case, then find first 1
    leading_zeros = (remaining_bits + '1').index('1')
    if bucket_id not in bucket_maxes or bucket_maxes[bucket_id] < leading_zeros:
        bucket_maxes[bucket_id] = leading_zeros
    i += 1
    if i % (read_num_lines/num_graph_samples) == 0:
        print(f'Sampling line {i} of {read_num_lines}')
        user_estimates.append(estimate_unique_users(bucket_maxes, m))
        user_estimates_x.append(i)

plt.plot(user_estimates_x, user_estimates)
plt.xlabel('Number of Lines Read')
plt.ylabel('Estimate of Total Unique Users')
plt.title('Convergence of Hyperloglog Estimate Over Time')
plt.savefig('q3_figure.png')

print(f'{estimate_unique_users(bucket_maxes, m)} estimated total unique users')



