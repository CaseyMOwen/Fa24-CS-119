#!/usr/bin/env python
import sys, shlex

def main(argv):
    line = sys.stdin.readline()
    try:
        while line:
            linelist = shlex.split(line)
            # Only consider input if we get full row exactly - may be slightly different if delimeter changes
            if len(linelist) == 11:
                response = linelist[6]
                response_type = response[0] + "00-" + response[0] + "99"
                print("ResponseType:" + response_type + "\t" + "1")
            line = sys.stdin.readline()
    except EOFError as error:
        return None

if __name__ == "__main__":
    main(sys.argv)

