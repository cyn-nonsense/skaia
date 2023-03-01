import http.client
import time
import unittest
import skaia
import json

TOKEN = json.load(open('password.json', 'r'))['TOKEN']


class SkaiaTest(unittest.TestCase):

    def setUp(self) -> None:
        skaia.Skaia.initialize()

    def test_one_user(self):
        skaia.JOIN_WINDOW_TIME_SECONDS = 2
        skaia.Skaia.queue = skaia.ServerQueue()
        username = "pretendThisIsSteam64"
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 0
        client.close()

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/add_users", json.dumps({"USERS": [username]}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 0

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/slots_opened", json.dumps({"COUNT": 1}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 1

        time.sleep(3)
        client.close()
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 0
        client.close()

    def test_huge_queue(self):
        skaia.JOIN_WINDOW_TIME_SECONDS = 2
        skaia.Skaia.queue = skaia.ServerQueue()
        users = ["asdf", "asdf2", "asdf3", "asdf4", "asdf5", "asdf6", "asdf7", "asdf8", "asdf9", "asdf10", "asdf11",
            "asdf12", "asdf13", "asdf14", "asdf15", "asdf16", "asdf17", "asdf18", "asdf19", "asdf20", ]
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 0
        client.close()

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/add_users", json.dumps({"USERS": users[:10]}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/slots_opened", json.dumps({"COUNT": 4}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()
        time.sleep(1)
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 4
        time.sleep(5)
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/slots_opened", json.dumps({"COUNT": 10}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()
        time.sleep(1)
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 6

        time.sleep(5)

        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("POST", "/add_users", json.dumps({"USERS": users[11:15]}),
                       {"Content-type": "text/plain", 'Token': TOKEN})
        client.close()
        time.sleep(1)
        client = http.client.HTTPConnection("127.0.0.1:8888")
        client.request("GET", "/open", headers={'Token': TOKEN})
        count = json.loads(client.getresponse().read().decode('utf-8'))["READY"]
        assert count == 4
        client.close()

if __name__ == '__main__':
    unittest.main()
