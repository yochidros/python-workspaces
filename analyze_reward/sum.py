import csv
import glob
import os

os.chdir('./csv')
res = glob.glob('amazon*.csv')

for file in res:
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        i = 0
        for item in reader:
            i += 1
            if item[5] != '0':
                print("{}, {}, {}, {}".format(file, item[0], item[5], i))
                break
