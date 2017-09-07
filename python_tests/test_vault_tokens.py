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

def run_ssh_command(command):
    sshCommand="ssh -q -i ~/.ssh/bitesize.key -oStrictHostKeyChecking=no centos@{0} \"{1}\"".format(master,command)
    #print(sshCommand)
    process = Popen(sshCommand, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    return stdout,stderr,errorCode

def test_a_create_test_ns():
    cmd="sudo kubectl create ns tokens-test && sudo /usr/local/bin/add_vault_tokens.sh tokens-test"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

def test_b_manually_verify_tokens():
    global readTokenTtl
    global writeTokenTtl
    global readToken
    global writeToken
    cmd="sudo kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o json | jq -r \'.data[]\' | base64 -d"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    readToken=stdout.rstrip()
    uuidPattern.match(readToken)
    cmd="sudo kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o json | jq -r \'.data[]\' | base64 -d"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    writeToken=stdout.rstrip()
    uuidPattern.match(writeToken)
    cmd="sudo su - -c \'vault token-lookup -format=json {0}\' | jq -r \'.data.ttl\'".format(readToken)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    readTokenTtl=stdout.rstrip()
    cmd="sudo su - -c \'vault token-lookup -format=json {0}\' | jq -r \'.data.ttl\'".format(writeToken)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    writeTokenTtl=stdout.rstrip()

def test_c_check_ns_tokens():
    global readTokenTtlNow
    global writeTokenTtlNow
    time.sleep(2)
    cmd="sudo su - -c \'/usr/local/bin/renew_vault_tokens.sh check tokens-test\' | grep ^TTL\: | awk \'{print \$2}\' | head -1"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    readTokenTtlNow=stdout.rstrip()
    cmd="sudo su - -c \'/usr/local/bin/renew_vault_tokens.sh check tokens-test\' | grep ^TTL\: | awk \'{print \$2}\' | tail -1"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    writeTokenTtlNow=stdout.rstrip()
    assert int(readTokenTtl) > int(readTokenTtlNow)
    assert int(writeTokenTtl) > int(writeTokenTtlNow)
    assert int(readTokenTtl) / int(readTokenTtlNow) == 1
    assert int(writeTokenTtl) / int(writeTokenTtlNow) == 1

def test_d_regen_tokens():
    cmd="sudo su - -c \'/usr/local/bin/renew_vault_tokens.sh regen tokens-test\'"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    cmd="sudo kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o json | jq -r \'.data[]\' | base64 -d"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    readTokenNew=stdout.rstrip()
    uuidPattern.match(readTokenNew)
    assert readTokenNew != readToken
    cmd="sudo kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o json | jq -r \'.data[]\' | base64 -d"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    writeTokenNew=stdout.rstrip()
    uuidPattern.match(writeTokenNew)
    assert writeTokenNew != writeToken
    cmd="sudo su - -c \'vault token-lookup -format=json {0}\' | jq -r \'.data.ttl\'".format(readTokenNew)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    readTokenNewTtl=stdout.rstrip()
    cmd="sudo su - -c \'vault token-lookup -format=json {0}\' | jq -r \'.data.ttl\'".format(writeTokenNew)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    writeTokenNewTtl=stdout.rstrip()

    assert int(readTokenNewTtl) > int(readTokenTtlNow)
    assert int(writeTokenNewTtl) > int(writeTokenTtlNow)

def test_e_delete_ns():
    cmd="sudo kubectl delete ns tokens-test"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    time.sleep(10)
    cmd="sudo su - -c \"/usr/local/bin/renew_vault_tokens.sh check tokens-test\""
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode != 0
