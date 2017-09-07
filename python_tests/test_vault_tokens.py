#!/usr/bin/python
import os
import re
import time
from subprocess import Popen, PIPE

master = os.environ["KUBERNETES_SERVICE_HOST"]
uuidPattern = re.compile("[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}")

readTokenTtl = 0
writeTokenTtl = 0
readTokenTtlNow = 0
writeTokenTtlNow = 0
readToken = ""
writeToken = ""

def run_script(command):
    global failuresReceived
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    return stdout,stderr,errorCode

def test_create_test_ns():
    cmd="ssh -i ~/.ssh/bitesize.key centos@{0} 'sudo kubectl create ns tokens-test && sudo /usr/local/bin/add_vault_tokens.sh tokens-test'".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0

def test_manually_verify_tokens():
    global readTokenTtl
    global writeTokenTtl
    global readToken
    global writeToken
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o json\' | jq -r \'.data[]\' | base64 -d".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    readToken=stdout.rstrip()
    uuidPattern.match(readToken)
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o json\' | jq -r \'.data[]\' | base64 -d".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    writeToken=stdout.rstrip()
    uuidPattern.match(writeToken)
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"vault token-lookup {1}\"\' | grep ^ttl | awk \'{{print $NF}}\'".format(master,readToken)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    readTokenTtl=stdout.rstrip()
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"vault token-lookup {1}\"\' | grep ^ttl | awk \'{{print $NF}}\'".format(master,writeToken)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    writeTokenTtl=stdout.rstrip()

def test_check_ns_tokens():
    global readTokenTtlNow
    global writeTokenTtlNow
    time.sleep(2)
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"/usr/local/bin/renew_vault_tokens.sh check tokens-test\"\' | grep ^TTL\: | awk \'{{print $2}}\' | head -1".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    readTokenTtlNow=stdout.rstrip()
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"/usr/local/bin/renew_vault_tokens.sh check tokens-test\"\' | grep ^TTL\: | awk \'{{print $2}}\' | tail -1".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    writeTokenTtlNow=stdout.rstrip()
    assert int(readTokenTtl) > int(readTokenTtlNow)
    assert int(writeTokenTtl) > int(writeTokenTtlNow)
    assert int(readTokenTtl) / int(readTokenTtlNow) == 1
    assert int(writeTokenTtl) / int(writeTokenTtlNow) == 1

def test_regen_tokens():
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"/usr/local/bin/renew_vault_tokens.sh regen tokens-test\"\'".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o json\' | jq -r \'.data[]\' | base64 -d".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    readTokenNew=stdout.rstrip()
    uuidPattern.match(readTokenNew)
    assert readTokenNew != readToken
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o json\' | jq -r \'.data[]\' | base64 -d".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    writeTokenNew=stdout.rstrip()
    uuidPattern.match(writeTokenNew)
    assert writeTokenNew != writeToken
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"vault token-lookup {1}\"\' | grep ^ttl | awk \'{{print $NF}}\'".format(master,readTokenNew)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    readTokenNewTtl=stdout.rstrip()
    cmd="ssh -q -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"vault token-lookup {1}\"\' | grep ^ttl | awk \'{{print $NF}}\'".format(master,writeTokenNew)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    writeTokenNewTtl=stdout.rstrip()

    assert int(readTokenNewTtl) > int(readTokenTtlNow)
    assert int(writeTokenNewTtl) > int(writeTokenTtlNow)

def test_delete_ns():
    cmd="ssh -i ~/.ssh/bitesize.key centos@{0} 'sudo kubectl delete ns tokens-test'".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode == 0
    time.sleep(10)
    cmd="ssh -i ~/.ssh/bitesize.key centos@{0} \'sudo su - -c \"/usr/local/bin/renew_vault_tokens.sh check tokens-test\"\'".format(master)
    stdout,stderr,errorCode=run_script(cmd)
    assert errorCode != 0
