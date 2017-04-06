#!/usr/bin/python
import boto3
import yaml
import requests
import json
import time

st2apikey = "NzlhYTFjNjE5ZGZhMTk1NGQxYzYzNzMwYTJjMTJiN2Y0OTg0MjJjMmJjMTNhNjdjY2QzNGUwZDU1NDQ5MmQ4MQ"

    

def test_stackstorm():
    hostYaml="/var/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("stackstorm" in host['name']):
                ip=host['value']

                checkfill(ip)

                errorCode,stderr=request_ns(ip)
                assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

                errorCode,stderr=create_project(ip)
                assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

def checkfill(st2host):
    errorCode,stderr = fill_consul(st2host, "bitesize/defaults/jenkinsversion", "3.4.35")
    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log
    errorCode,stderr = fill_consul(st2host, "bitesize/defaults/defaultdomain", "prsn-dev.io")
    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

def fill_consul(st2host, key, value):

    data = {"action": "consul.get",
            "user": None,
            "parameters": {"key": "bitesize/defaults/jenkinsversion"}
           }
    
    resp = run_st2(st2host, data)

    if resp[0] == 0:
        data = {"action": "consul.put",
                "user": None,
                "parameters": {
                    "key": key,
                    "value": value}
               }

    return run_st2(st2host, data)

def request_ns(st2host):

    data = {"action": "bitesize.request_ns",
            "user": None,
            "parameters": {
                "email": "test@test.com",
                "ns_list": ["dev"],
                "project": "kubetests",
                "gitrepo": "git@github.com:AndyMoore111/test-app-v2.git",
                "gitrequired": True}
           }

    return run_st2(st2host, data)

def create_project(st2host):

    data = {"action": "bitesize.create_project",
            "parameters": {
                "project": "kubetests"}
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
