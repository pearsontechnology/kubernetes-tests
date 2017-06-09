#!/usr/bin/python
import boto3
import os
import yaml
from subprocess import Popen, PIPE

def test_consul_read_and_write():
    hostYaml="/opt/testexecutor/hosts.yaml"
    env = os.environ["ENVIRONMENT"]
    dom = os.environ["DOMAIN"]
    token = os.environ["CONSUL_MASTER_TOKEN"]
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        hostYaml="/opt/testexecutor/hosts.yaml"
        with open(hostYaml, 'r') as ymlfile1:  # hosts to test
            contents = yaml.load(ymlfile1)
            for host in contents['hosts']:
                if ("master" in host['name']):
                    ip=host['value']

                    curlwrite = "curl -ks -X PUT -d 'test_value' https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2}".format(env,dom,token)
                    cmd="ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{0} '{1}'".format(ip,curlwrite)
                    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    errorCode = process.returncode
                    #print "Stdout:{0}".format(stdout)
                    #print "Stderr:{0}".format(stderr)
                    #print "errorCode:{0}".format(errorCode)
                    assert stdout == "true"

                    curlread = "curl -ks https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2} | jq '.[0].Value' | sed -e s/\"//g | base64 -d".format(env,dom,token)
                    cmd="ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{0} '{1}'".format(ip,curlread)
                    process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = process.communicate()
                    errorCode = process.returncode
                    #print "Stdout:{0}".format(stdout)
                    #print "Stderr:{0}".format(stderr)
                    #print "errorCode:{0}".format(errorCode)
                    assert stdout == "test_value"
