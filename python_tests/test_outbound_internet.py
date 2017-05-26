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

def test_outbound_internet_connectivity_from_minions(domain,ip):
    command = "ssh -i ~/.ssh/bitesize.key centos@{0} 'TIMEFORMAT=%R;time dig $domain'".format(ip)
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    return stderr
