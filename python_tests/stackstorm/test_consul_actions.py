import os
import sys
import unittest
import json

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from lib import st2


class TestConsulActions(unittest.TestCase):
    def setUp(self):
        host = os.getenv("ST2_ADDRESS")
        key = os.getenv("ST2_APIKEY")
        self.stackstorm = st2.Endpoint(host, key)

    def test_consul_get(self):
        params = {
            "key": "invalid_key"
        }
        data = self.assert_success_action("consul.get", params)
        self.assertEqual(data['result']['result'], None)

    def test_consul_put(self):

        params = {
            "key": "valid_key",
            "value": "valid_value"
        }
        self.assert_success_action("consul.put", params)

        params = { "key": "valid_key" }
        data = self.assert_success_action("consul.get", params)
        # This is ugly
        self.assertEqual(data['result']['result']['Value'], "valid_value")

    def test_consul_delete(self):
        params = {
            "key": "valid_key"
        }
        self.assert_success_action("consul.delete", params)

        # Could not get deleted key
        data = self.assert_success_action("consul.get", params)
        self.assertEqual(data['result']['result'], None)

    def assert_success_action(self, action, params):
        success, data = self.stackstorm.run_action(action, params)
        self.assertTrue(
            success,
            "{} failed.\n\tData: {}\n\tParams: {}\n".format(
                action,
                json.dumps(data),
                json.dumps(params)
            )
        )
        return data


if __name__ == "__main__":
    unittest.main(verbosity=2)
