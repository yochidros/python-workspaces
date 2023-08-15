import csv
import glob
import os
import re
os.chdir('./csv')
res = glob.glob('amazon*.csv')

arr = {}
for file in res:
    v = re.sub(r'_wifi_[0-9].csv', '', file)
    with open(file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        obj = []
        if v in arr:
            obj = arr[v]

        i = 0
        for item in reader:
            i += 1
            obj.append((i, item[0]))
            if item[5] != '0':
                break

        arr[v] = obj

for key, value in arr.items():
    res = {}
    for i, v in value:
        if i in res:
            res[i].append(v)
        else:
            res[i] = [v]
    with open('result.csv', 'a') as f:
        print(res)
        c = [len(k) for k in res.values()]
        c = [k for k in range(1, max(c)+1)]
        writer = csv.DictWriter(f, fieldnames=['name', 'order'] + c)
        data = {'name': key}
        writer.writerow(data)
        for i, va in res.items():
            obj = {'order': i}
            for j, v in enumerate(va):
                obj[j+1] = v
            print(obj)
            writer.writerow(obj)

