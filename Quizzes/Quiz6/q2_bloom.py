import sys
import base64
import numpy as np
import hashlib
from functools import reduce
import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

def get_bloom_match(word, bit_vec):
    '''
    Returns boolean indicating if the word hashes into a bucket in the bit_vec with a 1 in it.
    '''
    hash_object = hashlib.sha1()
    hash_object.update(word.encode('utf-8'))
    hash_int = int(hash_object.hexdigest(), 16)
    hash_idx = hash_int % len(bit_vec)
    return bool(bit_vec[hash_idx])


def is_good_line(line, bit_vec):
    '''
    Returns boolean indicating if a line contains any words that hash into the bit vector buckets provided.
    '''
    words = line.split(" ")
    bad_word_bools = list(map(lambda w: get_bloom_match(w, bit_vec), words))
    is_bad_line = reduce(lambda a,b: a or b, bad_word_bools)
    return not is_bad_line

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: q2_bloom.py <hostname> <port>", file=sys.stderr)
        sys.exit(-1)
    sc = SparkContext(appName="PythonStreamingBloomFilter")
    ssc = StreamingContext(sc, 1)
    
    # Load bit vector into list from hdfs
    bit_vec_string = sc.textFile("hdfs://quiz6-m.c.cs119-quiz-6.internal./bit_vector.txt").collect()[0]
    bit_array = np.frombuffer(base64.b64decode(bit_vec_string)).tolist()

    # Read lines, each as string in a row each in an rdd
    lines = ssc.socketTextStream(sys.argv[1], int(sys.argv[2]))

    # Filter each line according to whether it contains a bad word or not
    filtered_lines = lines.filter(lambda line: is_good_line(line, bit_array))
    filtered_lines.pprint()
    ssc.start()
    ssc.awaitTermination()