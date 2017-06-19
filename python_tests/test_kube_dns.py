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

def query_dns(domain,ip):
    command = "ssh -i ~/.ssh/bitesize.key centos@{0} 'TIMEFORMAT=%R;time dig $domain'".format(ip)
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    return stderr

def test_external_dns_query_performance():
        hostYaml="/opt/testexecutor/hosts.yaml"
        with open(hostYaml, 'r') as ymlfile1:  # hosts to test
            contents = yaml.load(ymlfile1)
            for host in contents['hosts']:
                if ("master" in host['name']):

                    ip=host['value']
                    sum=0
                    avgLookupTime=0

                    cmd="ssh -i ~/.ssh/bitesize.key centos@{0} 'ssh-keyscan {0} >> ~/.ssh/known_hosts > /dev/null 2>&1'".format(ip)
                    run_script(cmd, False)

                    sum+=float(query_dns("google.com",ip))
                    sum+=float(query_dns("pearson.com",ip))
                    sum+=float(query_dns("hipchat.com",ip))
                    sum+=float(query_dns("aws.com",ip))
                    sum+=float(query_dns("linkedin.com",ip))
                    avgLookupTime=sum/5
                    assert avgLookupTime < 0.200

def test_no_error_on_dns_lookup():
    hostYaml="/opt/testexecutor/hosts.yaml"
    with open(hostYaml, 'r') as ymlfile1:  # hosts to test
        contents = yaml.load(ymlfile1)
        for host in contents['hosts']:
            if ("master" in host['name']):
                command="ssh -i ~/.ssh/bitesize.key root@{0} 'dig google.com | grep -o 'status: NOERROR''".format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout, stderr = process.communicate()
                errorCode = process.returncode
                assert errorCode == 0   #If Error Code is zero, then the dig command returned with NOERROR status
