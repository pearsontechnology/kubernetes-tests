#!/usr/bin/python
import boto3
import os
import yaml
from subprocess import Popen, PIPE

def test_hello_world_app_is_accessable_through_bitesize_front_end():
    hostYaml="/opt/testexecutor/hosts.yaml"
    env = os.environ["ENVIRONMENT"]
    dom = os.environ["DOMAIN"]
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        hostYaml="/opt/testexecutor/hosts.yaml"
        with open(hostYaml, 'r') as ymlfile1:  # hosts to test
            contents = yaml.load(ymlfile1)
            for host in contents['hosts']:
                if ("master" in host['name']):
                    ip=host['value']
                    curlcmd = "curl -X POST -H \"Host: front.nodejs-hello-world-app.prsn-dev.io\" -H \"Content-Type: application/json\" -d \"{\\\"data\\\": \\\"blah\\\", \\\"username\\\": \\\"admin\\\", \\\"password\\\": \\\"password\\\"}\" http://front.nodejs-hello-world-app.${env}.${dom}"
                    cmd="ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{0} '{1}'".format(ip,curlcmd)

                    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    errorCode = process.returncode
                    #print "Stdout:{0}".format(stdout)
                    #print "Stderr:{0}".format(stderr)
                    #print "errorCode:{0}".format(errorCode)
                    assert stdout == "{\"status\":\"SUCCESS\"}"
