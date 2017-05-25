#!/usr/bin/python
import boto3
import os
from subprocess import Popen, PIPE
import yaml


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

def test_no_error_on_dns_lookup():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("minion" in host['name']):
                command="ssh -i ~/.ssh/bitesize.key centos@{0} 'ping -c 4 8.8.8.8 | grep -o '4 received''".format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                errorCode = process.returncode
                assert errorCode == 0   #If Error Code is zero, then the ping to Google DNS has received 4 return packets
