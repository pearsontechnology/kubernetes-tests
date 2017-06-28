import os
import sys
import json
import time
import requests

class Endpoint:
    def __init__(self, host, key):
        self.api_host = host
        self.api_key = key
        self.endpoint = "https://{}/api/v1/executions/".format(self.api_host)

        self.headers = {
            'St2-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        requests.packages.urllib3.disable_warnings()


    def run_action(self, action, params={}):
        data = json.dumps({
            "action": action,
            "user": None,
            "parameters": params
        })
        r = requests.post(self.endpoint, data=data, headers=self.headers, verify=False)
        response = json.loads(r.text)

        if 'faultstring' in response.keys():
            raise Exception(response['faultstring'])

        runner_id = response['id']

        return self.wait_for_completion(runner_id)


    def wait_for_completion(self, run_id):
        timeout = time.time() + 300
        checkurl = self.endpoint + run_id
        while time.time() < timeout:
            resp = requests.get(checkurl, headers=self.headers, verify=False)
            jdata = json.loads(resp.text)

            if jdata['status'] == "failed":
                return (False, jdata)

            if 'result' in jdata.keys() and 'tasks' in jdata['result'].keys():
                for job in jdata['result']['tasks']:
                    if job['state'] == "failed":
                        return (False, jdata)

            if jdata['status'] == "succeeded":
                return (True, jdata)

            time.sleep(2)

        return (False, "timeout waiting for job {} to complete".format(run_id))
