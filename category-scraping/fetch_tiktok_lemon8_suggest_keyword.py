import requests
import urllib.parse
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from queue import Queue
import sys


def fetch_suggest_word_lemon8(word):
    en_word = urllib.parse.quote(word.encode('utf8'))
    url = 'https://www.lemon8-app.com/api/200/web/sug_word/search?keyword={}&search_tab=main&sug_search_id=0&region=jp&device_platform=web&aid=2876'.format(en_word)
    response = requests.get(url)
    data = response.json()
    arr = []
    for v in data['data']['sugs']:
        w = v['text']
        arr.append(w)
    return arr


def fetch_suggest_word_tiktok(word):
    en_word = urllib.parse.quote(word.encode('utf8'))
    url = 'https://www.tiktok.com/api/search/general/preview/?aid=1988&app_language=ja&app_name=tiktok_web&browser_language=ja&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20%28Macintosh%29&channel=tiktok_web&cookie_enabled=true&device_id=7207369090665825794&device_platform=web_pc&focus_state=true&from_page=search&history_len=4&is_fullscreen=false&is_page_visible=true&keyword={}&os=mac&priority_region=&region=JP&tz_name=Asia%2FTokyo&webcast_language=ja-JP'.format(en_word)
    response = requests.get(url)
    data = response.json()
    arr = []
    for v in data['sug_list']:
        w = v['content']
        arr.append(w)
    return arr


def write_content(q):
    while True:
        if q.empty():
            break
        word = q.get()
        with open(sys.argv[2], 'a', newline='') as f:
            writer = csv.writer(f)
            for w in word[1]:
                writer.writerow([word[0], w, -1])

        q.task_done()
        print("done: {}".format(word[0]))


def run(*args):
    word = args[0]
    q = args[1]
    arr = [word]
    item = fetch_suggest_word_tiktok(word)
    item2 = fetch_suggest_word_lemon8(word)
    arr.extend(item)
    arr.extend(item2)
    q.put((word, list(dict.fromkeys(arr))))


if __name__ == '__main__':
    queue = Queue()
    words = []

    print(sys.argv[1])
    with open(sys.argv[1], 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        res = dict()
        for v in reader:
            words.append(v[1])
    t = threading.Thread(target=write_content, args=(queue,))
    t.start()

    with ThreadPoolExecutor(max_workers=6) as executor:
        tasks = [executor.submit(run, word, queue) for word in words]
        wait(tasks, return_when=ALL_COMPLETED)
        print("done")

    queue.join()
    t.join()
    print('all done')

