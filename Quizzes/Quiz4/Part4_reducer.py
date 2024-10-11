#!/usr/bin/env python
"""reducer.py"""

from operator import itemgetter
import sys

current_pres = None
current_pres_count = 0
current_pres_valence_sum = 0
pres = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    pres, valence = line.split('\t', 1)

    # convert count (currently a string) to int
    try:
        valence = int(valence)
    except ValueError:
        # count was not a number, so silently
        # ignore/discard this line
        continue
    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_pres == pres:
        current_pres_count += 1
        current_pres_valence_sum += valence
    else:
        if current_pres:
            avg_valence = current_pres_valence_sum/current_pres_count
            # write result to STDOUT
            print ('%s\t%s' % (current_pres, avg_valence))
        current_pres_count = 1
        current_pres_valence_sum = valence
        current_pres = pres

# do not forget to output the last word if needed!
# Avoid divide by zero error
if current_pres == pres and current_pres_count != 0:
    avg_valence = current_pres_valence_sum/current_pres_count
    print ('%s\t%s' % (current_pres, avg_valence))