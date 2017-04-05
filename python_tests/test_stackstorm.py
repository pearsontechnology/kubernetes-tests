#!/usr/bin/python
import boto3
import yaml
import requests
import json
import time

st2apikey = "OGNhYTM1YTUyYWY3Yjk2MjM3NmQwN2E1Mzc4Njc4MzFlZDNkODlkMzgwZWQ5ZGU1N2MxYjkwMWRjYzE0NmE1Yw"

def test_stackstorm():
    hostYaml="/var/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("stackstorm" in host['name']):
                ip=host['value']
                # Verify the Ansible Playbook Finished and there is no failures.  Look for the ansible RECAP and find any instances of failed=x where x is greater than zero
                errorCode,stderr=request_ns(ip)
                assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log
                errorCode,stderr=create_project(ip)
                assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log


def request_ns(st2host):

    data = {"action": "bitesize.request_ns",
            "user": None,
            "parameters": {
                "email": "test@test.com",
                "ns_list": ["dev"],
                "project": "kt",
                "gitrepo": "git@github.com:AndyMoore111/test-app-v2.git",
                "gitrequired": True}
           }

    return run_st2(st2host, data)

def create_project(st2host):

    data = {"action": "bitesize.create_project",
            "parameters": {
                "project": "kt"}
           }

    return run_st2(st2host, data)

def run_st2(st2host, data):

    executionsurl = "https://" + st2host + "/api/v1/executions/"

    headers = {'St2-Api-Key': st2apikey, 'Content-Type': 'application/json'}

    #print json.dumps(data, sort_keys=True, indent=2)
    #print json.dumps(headers, sort_keys=True, indent=2)

    #print executionsurl

    r = requests.post(executionsurl, data=json.dumps(data), headers=headers, verify=False)

    #print r.request.method
    #print r.history

    response = json.loads(r.text)
    print json.dumps(response, sort_keys=True, indent=2)
    runner_id = response['id']

    runcount = 0
    while True:
        runcount += 1

        checkurl = executionsurl + "/" + runner_id
        resp = requests.get(checkurl, headers=headers, verify=False)
        jdata = json.loads(resp.text)
        if jdata['status'] == "failed":
            return (0, "failed creating")
            for job in jdata['result']['tasks']:
                if job['state'] == "failed":
                    return (0, job['result']['stderr'])

        if runcount == 200:
            return (0, "timed out 10 mins")

        if jdata['status'] == "succeeded":
            return (1, "success")

        time.sleep(10)

    return (0, "unspecified error")
