import csv
import sys


def read(filename):
    with open(filename, 'r') as f:
        current = []
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            current.append((row[0], row[1], row[2], row[3]))
        return current

if __name__ == '__main__':
    current = read(sys.argv[1])
    name = sys.argv[1]
    value = sys.argv[2]
    print(name, value)

    if name in map(lambda x: x[0], current):
        print('The name is already in the list')
