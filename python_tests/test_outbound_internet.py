#!/usr/bin/python
import boto3
import os
from subprocess import Popen, PIPE
import yaml
import sys

def test_outbound_internet_connectivity_from_minions():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("minion" in host['name']):
                command="ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{0} 'curl -L -I www.google.com | grep -o '200 OK' | cut -c1-3'".format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                response = sys.stdout
                assert response == 200   #If the response is 200, Google returned a 200 OK
