#!/usr/bin/python
import boto3
import os
import yaml
from subprocess import Popen, PIPE

def run_script(command, output):
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
                # Verify the minions have outbound connectivity to the Internet by pinging Google DNS
                pingcount=host['value']
                cmd="ssh -i ~/.ssh/bitesize.key centos@{0} 'ping -c 4 8.8.8.8 | grep -o '[0-9] received' | cut -c1'".format(host['value'])
                stdout,stderr,errorCode=run_script(cmd)
                assert pingcount == 4 #If Ping Count is 4, then the ping to Google DNS has received 4 return packets
