#!usr/bin/env bash

./build/X86/gem5.opt \
		configs/example/se.py \
		--caches \
		--l2cache \
		--l1i_size=64kB \
		--l1d_size=64kB \
		--l1i_assoc=2 \
		--l1d_assoc=2 \
		--l2_size=256kB \
		--l3_size=10MB \
		--cpu-type=AtomicSimpleCPU \
		--sys-clock=2GHz \
		--cpu-clock=2GHz \
		--mem-type=DDR4_2400_8x8 \
		--mem-size=2GB \
		--cmd=/home/vagrant/gem5-experiments/benchmarks/STREAM-master/stream_c.exe

