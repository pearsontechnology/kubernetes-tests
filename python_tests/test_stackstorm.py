#!/usr/bin/python
import boto3
import yaml
import requests
import json
import time
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from uuid import UUID

domain=os.environ["DOMAIN"]
env = os.environ["ENVIRONMENT"]
st2pass = os.environ["ST2_PASSWORD"]

tokenurl = "https://stackstorm-prelive." + env + "." + domain + "/auth/v1/tokens"
r = requests.post(tokenurl, auth=("st2admin", st2pass), verify=False)
jdata = json.loads(r.text)
st2apitoken = jdata['token']

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_stackstorm():
    stack_id = os.environ["STACK_ID"]
    hostYaml="/opt/testexecutor/hosts.yaml"
    if (stack_id != 'b'):
        with open(hostYaml, 'r') as ymlfile1:  # hosts to test
            contents = yaml.load(ymlfile1)
            for host in contents['hosts']:
                if ("stackstorm" in host['name']):
                    ip=host['value']

                    checkfill(ip)

                    errorCode,stderr,_=request_ns(ip)
                    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

                    errorCode,stderr,_=create_project(ip)
                    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

                    check_keycloak_created(ip)

                    cleanup(ip)

                    check_keycloak_deleted(ip)

def check_keycloak_group(st2host, path):

    data = {"action": "keycloak.get_group_id",
            "user": None,
            "parameters": {"path": path}
           }

    return run_st2(st2host, data)


def checkfill(st2host):
    errorCode,stderr,_ = fill_consul(st2host, "bitesize/defaults/jenkinsversion", "3.4.35")
    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log
    errorCode,stderr,_ = fill_consul(st2host, "bitesize/defaults/defaultdomain", "prsn-dev.io")
    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

def fill_consul(st2host, key, value):

    data = {"action": "consul.get",
            "user": None,
            "parameters": {"key": key}
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

    env = os.environ["ENVIRONMENT"]
    data = {"action": "bitesize.request_ns",
            "user": None,
            "parameters": {
                "email": "test@test.com",
                "ns_list": ["dev"],
                "project": env + "-kubetests",
                "gitrepo": "git@github.com:AndyMoore111/test-app-v2.git",
                "gitrequired": True}
           }

    return run_st2(st2host, data)

def cleanup(st2host):

    errorCode,stderr,_=delete_project(st2host)
    assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

    check_keycloak_deleted(st2host)
    #errorCode,stderr,_=delete_r53(st2host)
    #assert errorCode != 0   #If Error Code is non-zere, then no Playbook/RECAP failures were found in the log

def delete_project(st2host):
    env = os.environ["ENVIRONMENT"]
    data = {"action": "bitesize.delete_project",
            "parameters": {
                "project": env + "-kubetests"}
           }

    return run_st2(st2host, data)

#def delete_r53(st2host):
#
#    env = os.environ["ENVIRONMENT"]
#    domain = os.environ["DOMAIN"]
#    cname = 'kubetests.' + env + '.' + domain
#
#    data = {"action": "aws.r53_zone_delete_cname",
#            "user": None,
#            "parameters": {
#                "name": cname,
#                "zone": domain}
#           }
#
#    return run_st2(st2host, data)

def create_project(st2host):
    env = os.environ["ENVIRONMENT"]
    data = {"action": "bitesize.create_project",
            "parameters": {
                "project": env + "-kubetests"}
           }

    return run_st2(st2host, data)

def check_keycloak_created(st2host):
    env = os.environ["ENVIRONMENT"]
    errorCode,stderr,result = check_keycloak_group(st2host, "/projects/" + env + "-kubetests")
    assert errorCode != 0
    try:
      assert UUID(result, version=4)
      return True
    except:
       return False

def check_keycloak_deleted(st2host):
    env = os.environ["ENVIRONMENT"]
    errorCode,stderr,result = check_keycloak_group(st2host, "/projects/" + env + "-kubetests")
    assert errorCode != 0
    try:
      assert not UUID(result, version=4)
      return True
    except:
       return False

def run_st2(st2host, data):

    executionsurl = "https://" + st2host + "/api/v1/executions/"

    headers = {'X-Auth-Token': st2apitoken, 'Content-Type': 'application/json'}

    #print json.dumps(data, sort_keys=True, indent=2)
    #print json.dumps(headers, sort_keys=True, indent=2)

    #print executionsurl

    r = requests.post(executionsurl, data=json.dumps(data), headers=headers, verify=False)

    #print r.request.method
    #print r.history

    response = json.loads(r.text)
    #print json.dumps(response, sort_keys=True, indent=2)
    runner_id = response['id']

    runcount = 0
    while True:
        runcount += 1

        checkurl = executionsurl + "/" + runner_id
        resp = requests.get(checkurl, headers=headers, verify=False)
        jdata = json.loads(resp.text)
        if jdata['status'] == "failed":
            return (0, "failed creating", None)
            for job in jdata['result']['tasks']:
                if job['state'] == "failed":
                    return (0, job['result']['stderr'], None)

        if runcount == 200:
            return (0, "timed out 10 mins", "timed out")

        if jdata['status'] == "succeeded":
            try:
                result = jdata['result']['result']
            except:
                result = jdata['status']
            return (1, "success", result)

        time.sleep(10)

    return (0, "unspecified error", "failed")
