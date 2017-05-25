#!/usr/bin/python
import boto3
import os
import yaml
from subprocess import Popen, PIPE

def run_script(command):
    global failuresReceived
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    return stdout,stderr,errorCode

def test_outbound_internet_connectivity_from_minions():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("minion" in host['name']):
                # Verify outbound Internet connectivity from minion hosts by ping to 8.8.8.8 (Google DNS)
                command="ssh -i ~/.ssh/bitesize.key centos@{0} 'ping -c 1 8.8.8.8 | grep -o '0 received''".format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout, stderr, errorCode=run_script(cmd)
                assert errorCode != 0   #If Error Code is non-zere, then a minion does not have outbound connectivity to the Internet
