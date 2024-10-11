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
                # Is a client error if the response code starts with a 4
                if response[0] == '4':
                    ip_address = linelist[0]
                    print("IPAddress:" + ip_address + "\t" + "1")
            line = sys.stdin.readline()
    except EOFError as error:
        return None

if __name__ == "__main__":
    main(sys.argv)

