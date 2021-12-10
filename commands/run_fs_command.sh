#!usr/bin/env bash

export IMG_ROOT=/home/vagrant/software/gem5/fs_images

bootloader='boot.arm'
kernel='vmlinux.arm'
disc='m5_exit.squashfs.arm' 

echo "gem5 fs bigLITTLE with $bootloader bootloader $kernel kernel and $disc disc"

./build/ARM/gem5.opt configs/example/arm/fs_bigLITTLE.py \
	   	--caches \
		--bootloader="$IMG_ROOT/binaries/$bootloader" \
		--kernel="$IMG_ROOT/binaries/$kernel" \
		--disk="$IMG_ROOT/disks/$disc" \
		--bootscript="./configs/boot/bbench-gb.rcS"

