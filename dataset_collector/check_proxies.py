import threading
import queue
import requests

q = queue.Queue()
valid_proxies = []

with open(r"C:\xampp\htdocs\GitHub\Chiron\dataset_collector\proxies.txt", 'r') as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)


def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get("http://ipinfo.io/json", 
                               proxies={ "http": proxy, "https": proxy}, timeout=5)
        except:
            continue

        # if res.status_code == 200:
        #     print(proxy)
        if res.status_code == 200:
            print(f"'{proxy}'")

for _ in range(10):
    threading.Thread(target=check_proxies).start()