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
                command="ssh -i ~/.ssh/bitesize.key root@{0} 'curl -L -I www.google.com | grep -o '200' | head -n 1".format(host['value'])
                process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                stdout,stderr,errorCode=run_script(command)
                returncode = sys.stdout
                assert returncode == 200   #If returncode = 200, www.google.com returns 200 OK
