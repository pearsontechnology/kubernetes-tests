#!/usr/bin/python
import boto3
import os
from subprocess import Popen, PIPE
import yaml

def test_outbound_internet_connectivity_from_minions():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("minion" in host['name']):
                command = """ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{} "curl -L -I www.google.com | grep -o '200 OK'" """.format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                response = process.stdout.read()
                print response
                if response.rstrip() ! == '200 OK':
                    raise Exception('No response from www.google.com')
