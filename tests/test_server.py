import unittest

from toripchanger import server


class TestTorIpChangerServer(unittest.TestCase):
    def setUp(self):
        self.tor_ip_changer = unittest.mock.Mock()
        app = server.init_server(self.tor_ip_changer)
        app.testing = True

        self.client = app.test_client()

    def test_index(self):
        """
        Test `/` endpoint returns a simple text message.
        """
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data.decode("utf-8"), "TorIpChanger Server")

    def test_changeip(self):
        """
        Test `/changeip/` endpoint is capable of changing Tor' IP.
        """
        self.tor_ip_changer.get_new_ip.return_value = "1.2.3.4"
        r = self.client.get("/changeip/")

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json, {"newIp": "1.2.3.4", "error": ""})

    def test_changeip_exception(self):
        """
        Test `/changeip/` gracefully handles all exceptions.
        """
        self.tor_ip_changer.get_new_ip.side_effect = [ValueError("message")]
        r = self.client.get("/changeip/")

        self.assertEqual(r.status_code, 500)
        self.assertEqual(
            r.json, {"error": "<class 'ValueError'>: message", "newIp": ""}
        )
