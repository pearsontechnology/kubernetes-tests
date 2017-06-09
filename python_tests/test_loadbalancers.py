#!/usr/bin/python
import boto3
import os

##Verify both front-end live and pre-live loadbalancers are running
def test_loadbalancers_exist():
    elb = boto3.client('elb', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    frontendprelive = "frontend-" + env + "-prelive"
    frontendlive = "frontend-" + env + "-live"
    stackstormprelive = "stackstorm-" + env + "-prelive"
    stackstormlive = "stackstorm-" + env + "-live"
    masterprelive = "master-" + env + "-prelive"
    masterlive = "master-" + env + "-live"
    bastion = "bastion-" + env
    consul = "consul-bitesize-" + env
    vault = "vault-bitesize-" + env
    bals=elb.describe_load_balancers()
    lbcount=0
    for elb in bals['LoadBalancerDescriptions']:
        if (elb['LoadBalancerName'] == frontendprelive): lbcount += 1
        if (elb['LoadBalancerName'] == frontendlive): lbcount += 1
        if (elb['LoadBalancerName'] == stackstormprelive): lbcount += 1
        if (elb['LoadBalancerName'] == stackstormlive): lbcount += 1
        if (elb['LoadBalancerName'] == masterprelive): lbcount += 1
        if (elb['LoadBalancerName'] == masterlive): lbcount += 1
        if (elb['LoadBalancerName'] == bastion): lbcount += 1
        if (elb['LoadBalancerName'] == consul): lbcount += 1
        if (elb['LoadBalancerName'] == vault): lbcount += 1
    assert lbcount ==  9
