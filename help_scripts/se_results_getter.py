import shutil
import os

initialDir = '/home/vagrant/gem5-experiments/m5out'
outDir = '/home/vagrant/gem5-experiments/my_runs'

# Walk through m5out for interesting outputs
for root, dirs, files in os.walk(initialDir):
    for filename in files:
        
        # Complete path with old name
        old_name = os.path.join(os.path.abspath(root), filename)

        # Separate base from extension
        base, extension = os.path.splitext(filename)

        # New name
        new_name = os.path.join(outDir, base, filename)
        print(new_name)

        # If folder does not exist, create it
        if not os.path.exists(os.path.join(outDir, base)):
            print(os.path.join(outDir, base), "Not found")
            continue # Next filename
        # Folder exists, the file does not
        elif not os.path.exists(new_name):
             shutil.copy(old_name, new_name)
           # Folder exists and so does the file
        else:
            ii = 1
            while True:
                new_name = os.path.join(outDir, base, base + "_" + str(ii) + extension)
                if not os.path.exists(new_name):
                    shutil.copy(old_name, new_name)
                    print("Copied", old_name, "as", new_name)
                    break
                ii += 1
