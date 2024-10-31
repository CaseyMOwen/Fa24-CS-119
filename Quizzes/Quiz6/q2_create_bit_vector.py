#!/usr/bin/env python3

import requests
import numpy as np
import hashlib
import base64

bit_vector_size = 1500
bit_vector = np.zeros(bit_vector_size)
afinn = requests.get('https://raw.githubusercontent.com/fnielsen/afinn/master/afinn/data/AFINN-en-165.txt').content.decode().splitlines()
afinn_dict = dict(map(lambda x: (x.split('\t')), afinn))
for word in afinn_dict:
    if afinn_dict[word] in ['-4', '-5']:
        hash_object = hashlib.sha1()
        hash_object.update(word.encode('utf-8'))
        hash_int = int(hash_object.hexdigest(), 16)
        hash_idx = hash_int % bit_vector_size
        bit_vector[hash_idx] = 1

array_bytes = bit_vector.tobytes()
base64_string = base64.b64encode(array_bytes).decode('utf8')

with open('bit_vector.txt', "w") as f:
    f.write(base64_string)