#!/usr/bin/python

from subprocess import Popen, PIPE
import sys
import nose2
import yaml
import argparse
import os
import time
from github import Github
import urlparse
import urllib

from multiprocessing import Pool

pythonNoseDir = "/tmp/kubernetes-tests/python_tests"
batsDir = "/tmp/kubernetes-tests/bats_tests/"
inspecDir = "/tmp/kubernetes-tests/inspec_tests/controls/"
inspecConfig = "/tmp/kubernetes-tests/inspec_tests/config.yaml"
failuresReceived = False

GIT_USERNAME = os.environ['GIT_USERNAME']
GIT_PASSWORD = os.environ['GIT_PASSWORD']
GIT_REPO = os.environ['GIT_REPO']
GIT_BRANCH = os.environ['GIT_BRANCH']

g = Github(GIT_USERNAME, GIT_PASSWORD)

def clone_repo(name, url, directory):
    parts = urlparse.urlparse(url)
    netloc = parts.netloc
    encoded_username = urllib.quote(GIT_USERNAME)
    encoded_password = urllib.quote(GIT_PASSWORD)
    location_with_password = '{0}:{1}@{2}'.format(encoded_username, encoded_password, netloc)
    parts = parts._replace(netloc=location_with_password)
    auth_url = parts.geturl()
    command = "git clone --branch " + GIT_BRANCH + " " + auth_url + " " + directory
    print("Cloning Repo = {0}".format(command))
    run_script(command,True)

def str_to_bool(s):
    s.lower() == "true"

def print_test_msg(testType):
    print ("**********************************************************")
    print ("Executing %s Tests" % (testType))
    print ("**********************************************************")

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

def run_tests_for_kind(kind):



def executeTest(hostname, ip, testFiles=None):
    with open(inspecConfig, 'r') as ymlfile2:
        cfg = yaml.load(ymlfile2)
        for resourceName in cfg:
            if (cfg[resourceName] is None):
                continue
            if resourceName is not in hostname:
                continue

            for test in cfg[resourceName]:
                cmd = "echo \"Host {0}\n\tStrictHostKeyChecking no\n\" >> ~/.ssh/config".format(ip)
                run_script(cmd, False)
                if shouldRunTest(test, testFiles):
                    username = "centos"
                    if resourcename in ["nfs","bastion","stackstorm"]:
                        username = "root"
                    cmd = "inspec exec {0}{1} -t \"ssh://{2}@{3}\" --key-files=\"~/.ssh/bitesize.key\"".format(inspecDir, test, username, ip)
                    print("Testing on HostName=%s with IP=%s" % (hostname, ip))
                    print("    Command = %s " % (cmd))
                    run_script(cmd, True)

def shouldRunTest(test, testFiles):
    if testFiles is None:
        return true
    if (testfiles is not None) and (test in testFiles):
        return true
    return false

def executeInspecTests(testType, testFiles):
    hosts = hostsFromFile(hostYaml)

    # construct function arguments for parallel processing with Pool.map
    args = map(lambda host: [host, testFiles], hosts)

    with Pool(10) as p:
        p.map(executeInspecTestForHost, args)

def executeInspecTestForHost(host, testType, testFiles):
    if testType is None:
        executeTest(host['name'], host['value'])
    elif testType == "inspec":
        executeTest(host['name'], host['value'], testFiles)


def executePythonTests(testType, testFiles):
    if testType is None:
        print_test_msg("Python")
        run_script("nose2 -s %s -v" % (pythonNoseDir), True)
    elif testType == "python":
        print_test_msg("Python")
        for test in testFiles:
            run_script("nose2 -s %s -v %s" % (pythonNoseDir,test), True)


def hostsFromFile(filename):
    with open(filename, 'r') as yml:
        try:
            contents = yaml.load(yml)
            return contents['hosts']
        except:
            return []

def executeBatsTests(testType, testFiles):

    if testType is None:
        print_test_msg("Bats")
        run_script("bats %s" % (batsDir), True)
    elif testType == "bats":
        print_test_msg("Bats")
        for test in testFiles:
            t = batsDir + test
            run_script("bats %s" % (t), True)

parser = argparse.ArgumentParser()
parser.add_argument("config", help="config - Key/Value Yaml File containing hostnames ad :ips' to test")
parser.add_argument("type", nargs='?', help="type - Type of files to test (python,inspec,bats)")
parser.add_argument("files", nargs='*', help="files - Files to test")
parser.add_argument("target", nargs='?', help="target - Target to run tests against (stackstorm, master, minion)")
args = parser.parse_args()
hostYaml = args.config
testType = args.type
testFiles = args.files


#print("Host Yaml= %s" % (hostYaml))
#print("Test Type= %s" % (testType))
#print("Test Files= %s" % (testFiles))

clone_repo("kubernetes-tests", "https://github.com/pearsontechnology/kubernetes-tests.git", "/tmp/kubernetes-tests")

if args.kind is not None:
    #TODO
    run_tests_for_kind(args.kind)
else:
    executeInspecTests(testType, testFiles)
    executePythonTests(testType, testFiles)
executeBatsTests(testType, testFiles)

if(failuresReceived):
    print ("**********************************************************")
    print ("Errors/Failures Received During Containerized Tests")
    print ("**********************************************************")
    sys.exit(1)
