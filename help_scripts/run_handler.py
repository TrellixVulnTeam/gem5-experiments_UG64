import shutil
import os
import subprocess
from datetime import date
import inputs

initialDir = '/home/vagrant/gem5-experiments/help_scripts/m5out'
runsDir = '/home/vagrant/gem5-experiments/my_runs'
i = 0

for l1is, l1ds, l1ia, l1da in zip(inputs.l1i_size, inputs.l1d_size, inputs.l1i_assoc, inputs.l1d_assoc):
    # Runs the gem5 cmd and wait for it to finish
    cmd =[  f'/home/vagrant/gem5-experiments/build/{inputs.isa}/gem5.opt', 
            '/home/vagrant/gem5-experiments/configs/example/se.py',
            '--caches',
            f'--l1i_size={l1is}',
            f'--l1d_size={l1ds}',
            f'--l1i_assoc={l1ia}',
            f'--l1d_assoc={l1da}',
            '--sys-clock=2GHz',
            '--cpu-clock=2GHz',
            '--mem-type=DDR4_2400_8x8',
            '--mem-size=2GB',
            '--cmd=/home/vagrant/gem5-experiments/benchmarks/STREAM-master/stream_c.exe']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    print(subprocess.list2cmdline(cmd))
    for line in p.stdout:
        print(line)
    p.wait()
    print(p.returncode)

    # Create a new directory for the current run results
    newRunDir = os.path.join(runsDir, inputs.baseName + "_" + str(i))
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
    i += 1
