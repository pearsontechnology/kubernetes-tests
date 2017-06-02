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
    #cmd = "curl -s -m 5 -o /dev/null -w \"%{http_code}\" -X POST -H 'Host: front.nodejs-hello-world-app.prsn-dev.io' -H \"Content-Type: application/json\" -d '{\"data\": \"blah\", \"username\": \"admin\", \"password\": \"password\"}' http://front.nodejs-hello-world-app.prsn-dev.io | grep 200"
    cmd = "curl -X POST -H 'Host: front.nodejs-hello-world-app.prsn-dev.io' -H \"Content-Type: application/json\" -d '{\"data\": \"blah\", \"username\": \"admin\", \"password\": \"password\"}' http://front.nodejs-hello-world-app.prsn-dev.io"
    stdout = run_script(cmd, False)
    #print "Stdout: {0}".format(stdout[0])
    assert stdout[0] == "{\"status\":\"SUCCESS\"}"
