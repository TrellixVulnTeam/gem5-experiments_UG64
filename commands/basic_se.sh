#!usr/bin/env bash

# Command and option take benchmark values.
command = ''
option = ''

gem5/build/X86/gem5.opt gem5/configs/example/se.py --cmd=$command --options="$options" --l1d-hwp-type=StridePrefetcher --l2-hwp-type=BOPPrefetcher --cpu-type=DerivO3CPU --mem-type=DDR4_2400_16x4 --caches --l2cache --mem-size=10GB
