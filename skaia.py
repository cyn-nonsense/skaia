import http
from http.client import HTTPConnection
from threading import Thread, Lock
from typing import List, Callable, Dict
from collections import deque
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import socket
import os
import time


TOKEN = json.load(open('password.json', 'r'))['TOKEN']


JOIN_WINDOW_TIME_SECONDS = 15


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class ServerQueue:
    def __init__(self):
        self.lock = Lock()
        self.queue: List[str] = []
        self.neg_open = 0
        self.currently_open_for: List[str] = []
        self.slot_timeouts: Dict[str, int] = {}

    def add_to_queue(self, item):
        print(f'Added {item}')
        self.queue.append(item)

    def pop_n_users(self, count):
        while len(self.queue) > 0 and count > 0:
            it = self.queue.pop(0)
            self.currently_open_for.append(it)
            print(f'Serving {it}')
            self.slot_timeouts[it] = int(time.time()) + JOIN_WINDOW_TIME_SECONDS
            count -= 1

        self.neg_open += count
        print(f'neg = {self.neg_open}')

    def get_allowed_users(self) -> List[str]:
        now = int(time.time())
        r = []
        while len(self.queue) > 0 and self.neg_open > 0:
            it = self.queue.pop(0)
            self.currently_open_for.append(it)
            print(f'Serving {it}')
            self.slot_timeouts[it] = int(time.time()) + JOIN_WINDOW_TIME_SECONDS
            self.neg_open -= 1
            print(f'neg = {self.neg_open}')
        for i, user in enumerate([x for x in self.currently_open_for]):
            if self.slot_timeouts[user] < now:
                del self.slot_timeouts[user]
                self.currently_open_for.remove(user)
                print(f'Evicted {user}')
            else:
                r.append(user)
        return r


class DerseHandler:
    def __init__(self):
        pass


class Skaia(BaseHTTPRequestHandler):
    queue = ServerQueue()

    @classmethod
    def initialize(cls):
        Thread(target=cls._initialize, args=[]).start()

    @classmethod
    def _initialize(cls):
        server = ThreadingHTTPServer(("127.0.0.1", 8888), Skaia)
        print('[+] Online.')
        server.serve_forever()

    def do_POST(self):
        if self.headers['Token'] != TOKEN:
            self.send_response(400)
            self.end_headers()
            return

        body: bytes = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        if self.path == "/add_users":
            users = json.loads(body)["USERS"]
            for user in users:
                self.queue.add_to_queue(user)

        if self.path == "/slots_opened":
            count = int(json.loads(body)["COUNT"])
            self.queue.pop_n_users(count)

    def do_GET(self):
        if self.path == "/open":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            users = self.queue.get_allowed_users()
            out_data = json.dumps({
                'TYPE': 'OPEN',
                'READY': len(users),
                'USERS': users
            })
            self.wfile.write(out_data.encode('utf-8'))
            return

        if self.path == "/full_queue":
            if self.headers['Token'] != TOKEN:
                self.send_response(400)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()

            users = self.queue.get_allowed_users()
            out_data = json.dumps({
                'TYPE': 'FULL',
                'COUNT': len(self.queue.queue),
                'USERS': self.queue.queue,
                'READY': len(users),
                'CANJOIN': users
            })

            self.wfile.write(out_data.encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()


if __name__ == '__main__':
    Skaia.initialize()
