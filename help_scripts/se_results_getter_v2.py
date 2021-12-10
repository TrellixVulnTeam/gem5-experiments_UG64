import shutil
import os
import subprocess
from datetime import date

initialDir = '/home/vagrant/gem5-experiments/m5out'
runsDir = '/home/vagrant/gem5-experiments/my_runs'
cmdDir = '/home/vagrant/gem5-experiments/commands'
baseName = input("Runs default name: ")
# Make 10 runs, cp the config and stats for each runs in a dedicated folder


for i in range(10):
    # Runs the gem5 cmd and wait for it to finish
    cmd = ['/home/vagrant/gem5-experiments/build/X86/gem5.opt \
            /home/vagrant/gem5-experiments/configs/example/se.py \
            --caches \
            --l1i_size=32MB \
            --l1d_size=32MB \
            --l1i_assoc=2 \
            --l1d_assoc=2 \
            --sys-clock=2GHz \
            --cpu-clock=2GHz \
            --mem-type=DDR4_2400_8x8 \
            --mem-size=2GB \
            --cmd=/home/vagrant/gem5-experiments/benchmarks/STREAM-master/stream_c.exe']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    for line in p.stdout:
        print(line)
    p.wait()
    print(p.returncode)

    # Create a new directory for the current run results
    newRunDir = os.path.join(runsDir, baseName + "_" + str(i))
    # Created the new directory
    if not os.path.exists(newRunDir):
        os.makedirs(newRunDir)

    # Copy gem5 ouputs in the new directory
    out_files = os.listdir(initialDir)
    for file_name in out_files:
        full_file_name = os.path.join(initialDir, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, newRunDir)
    print("Run number: ", i)
