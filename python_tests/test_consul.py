#!/usr/bin/python
import boto3
import os
import yaml
from subprocess import Popen, PIPE

try:
    stack = os.environ["STACK_ID"]
except:
    stack = "a"

env = os.environ["ENVIRONMENT"]
dom = os.environ["DOMAIN"]
token = os.environ["CONSUL_MASTER_TOKEN"]

master = "master-" + stack + "." + env + ".kube"

testValue="test_value"

def run_ssh_command(command):
    sshCommand="ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@{0} \"{1}\"".format(master,command)
    #print(sshCommand)
    process = Popen(sshCommand, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    errorCode = process.returncode
    #print "Stdout:{0}".format(stdout)
    #print "Stderr:{0}".format(stderr)
    #print "errorCode:{0}".format(errorCode)
    return stdout,stderr,errorCode

def test_a_consul_read_and_write():
    cmd = "curl -ks -X PUT -d '{3}' https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2}".format(env,dom,token,testValue)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

    cmd = "curl -ks https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2} | jq '.[0].Value'".format(env,dom,token)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

    cmd = "curl -s http://consul.bitesize.{0}.{1}:8500/v1/kv/test/KEY1?token={2} | jq '.[0].Value'".format(env,dom,token)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

    cmd = "curl -fks https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1".format(env,dom)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode != 0

def test_b_backup_consul():
    cmd="sudo su - -c \'/usr/local/bin/backup_consul.sh\'"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

def test_c_delete_test_value():
    cmd="curl -ks -X DELETE https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2}".format(env,dom,token)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

def test_d_restore_consul():
    cmd="echo y | sudo su - -c \'/usr/local/bin/backup_consul.sh restore\'"
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0

def test_e_read_test_value():
    cmd="curl -ks -X GET https://consul.bitesize.{0}.{1}/v1/kv/test/KEY1?token={2} | jq -r \'.[].Value\' | base64 -d".format(env,dom,token)
    stdout,stderr,errorCode=run_ssh_command(cmd)
    assert errorCode == 0
    testValueResp=stdout.rstrip()
    assert testValueResp == testValue
