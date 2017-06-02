#!/usr/bin/python
import boto3
import os
from subprocess import Popen, PIPE


def run_script(command, output):
    global failuresReceived
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    if(errorCode != 0):
        failuresReceived = True
    if(output):
        #print "Received Error Code: {0}".format(errorCode)
        print "{0}".format(stdout)
        print "{0}".format(stderr)
    return stdout, stderr, errorCode

def test_hello_world_app_responds_through_bitesize_front_end():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("master" in host['name']):
                ip=host['value']
                curl = "curl -m 5 -X POST -H 'Host: front.nodejs-hello-world-app.prsn-dev.io' -H \"Content-Type: application/json\" -d '{\"data\": \"blah\", \"username\": \"admin\", \"password\": \"password\"}' http://front.nodejs-hello-world-app.prsn-dev.io"
                cmd="ssh -i ~/.ssh/bitesize.key centos@{0} '{1}'".format(ip,curl)
                stdout = run_script(cmd, False)
                #print "Stdout: {0}".format(stdout[0])
                assert stdout[0] == "{\"status\":\"SUCCESS\"}"
