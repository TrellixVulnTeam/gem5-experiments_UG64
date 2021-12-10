#!usr/bin/env bash

./build/X86/gem5.opt \
		configs/example/se.py \
		--caches \
		--l1i_size=32MB \
		--l1d_size=32MB \
		--l1i_assoc=2 \
		--l1d_assoc=2 \
		--sys-clock=2GHz \
		--cpu-clock=2GHz \
		--mem-type=DDR4_2400_8x8 \
		--mem-size=2GB \
		--cmd=/home/vagrant/software/gem5/benchmarks/STREAM-master/stream_c.exe

