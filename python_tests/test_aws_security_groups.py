#!/usr/bin/python
import unittest
import boto3
import os

class TestSecurityGroups(unittest.TestCase):

  def testNoInboundFromAny(self):
      env = os.environ["ENVIRONMENT"]
      region = os.environ["REGION"]
      client = boto3.client('ec2', region_name=region)
      security_groups = client.describe_security_groups(Filters = [{'Name':'tag:Name', 'Values': ['*'+ env + '*']}])
      any_count = 0
      print ('security groups with a rule allowing inbound from any IP address are:')
      for security_group in security_groups ['SecurityGroups']:
        #uncomment lines below to debug
        #print (security_group['GroupId'])
        #print (security_group['GroupName'])
        #print (security_group['IpPermissions'])
        sg_id = security_group['GroupId']
        my_security_groups = client.describe_security_groups(GroupIds = [sg_id], Filters = [{'Name': 'ip-permission.cidr', 'Values': ['0.0.0.0/0']}])
        for my_security_group in my_security_groups ['SecurityGroups']:
            print ('  ' + my_security_group ['GroupName'])
            any_count +=1
      assert any_count == 1   # only the external ELB security group should allow inbound from any IP address

if __name__ == '__main__':
    unittest.main()
