import requests
import urllib.parse
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue
import sys
import os

BASE_URL = os.environ['KEYWORD_URL']


def fetch_keyword_count(word):
    en_word = urllib.parse.quote(word.encode('utf8'))
    url = BASE_URL + '&query={}'.format(en_word)
    response = requests.get(url)
    data = response.json()
    count = int(data['meta']['actual-total-count'])
    return count


def write_content(q):
    while True:
        word = q.get()
        length = 0
        with open(sys.argv[2], 'a', newline='') as f:
            writer = csv.writer(f)
            rows = [(w[0], w[1], w[2]) for w in word]
            length = len(rows)
            writer.writerows(rows)

        q.task_done()
        print("done: {}".format(length))
        if q.empty():
            break


def run(*args):
    words = args[0]
    if len(words) == 0:
        return
    q = args[1]
    res = []
    print('fetching contents count {}'.format(len(words)))
    for w in words:
        base_word = w[0]
        word = w[1]
        count = fetch_keyword_count(word)
        res.append((base_word, word, count))
    q.put(res)
    print('put values into write result')


if __name__ == '__main__':
    queue = Queue()
    words = []

    excluded = []
    with open(sys.argv[2], 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for v in reader:
            excluded.append(v[1])

    with open(sys.argv[1], 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for v in reader:
            if int(v[2]) == -1 and v[1] not in excluded:
                words.append((v[0], v[1]))

    if len(words) == 0:
        print("empty")
        sys.exit(1)

    print(len(words))

    t = threading.Thread(target=write_content, args=(queue,))
    t.start()

    length = len(words)
    arr = []
    if length > 400:
        n = 0
        # 分割する変数の個数を指定
        s = 400

        # 配列を指定した個数で分割していくループ処理
        for i in range(0, length):
            arr.append(words[n:n+s:1])
            n += s

            # カウント数が配列の長さを超えたらループ終了
            if n >= length:
                break
    else:
        arr = words

    print('splited: {}'.format(len(arr)))

    with ThreadPoolExecutor(max_workers=100) as executor:
        tasks = [executor.submit(run, word, queue) for word in arr]
        wait(tasks, return_when=ALL_COMPLETED)
        print("tasks done")

    queue.join()
    t.join()
    print('all done')
