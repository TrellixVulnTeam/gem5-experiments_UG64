#!usr/bin/env bash

# get somewhat usefull information about the run

grep -rnw "size" m5out/config.ini | head -n 1
grep -rn assoc m5out/config.ini | head -n 4
grep -rnw "overallMissRate" m5out/stats.txt
grep -rnw "simSeconds" m5out/stats.txt
grep -rnw "hostSeconds" m5out/stats.txt
