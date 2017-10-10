#!/usr/bin/python
import boto3
import json
import os
import unittest

class TestAWSIamPolicies(unittest.TestCase):

    def testAssumeRoleFromAnyAWSAccount(self):
        region = os.environ["REGION"]
        client = boto3.client('iam', region_name=region)
        env = os.environ["ENVIRONMENT"]
        any_count = 0
        for role in client.list_roles(MaxItems=1000)['Roles']:
            if role['RoleName'].startswith(env + '-') or role['RoleName'].startswith('etcd-' + env):
                role_name = role['RoleName']
                #uncomment the line below for troubleshooting
                #print role_name
                allstmt = role['AssumeRolePolicyDocument']['Statement']
                for stmt in allstmt:
                    if 'AWS' in stmt['Principal'] and stmt['Principal']['AWS'] == '*':
                        print ('IAM role with aws:* :')
                        print role_name
                        any_count +=1
        assert any_count == 0   # AssumeRole from any AWS account not allowed

    def testManagedPolicyWildcards(self):
        region = os.environ["REGION"]
        client = boto3.client('iam', region_name=region)
        env = os.environ["ENVIRONMENT"]
        wildcard_count = 0
        for role in client.list_roles(MaxItems=1000)['Roles']:
            if role['RoleName'].startswith(env + '-') or role['RoleName'].startswith('etcd-' + env):
                role_name = role['RoleName']
                #uncomment the line below for troubleshooting
                #print role_name
                for attached_policy in client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']:
                    attached_policy_arn = attached_policy['PolicyArn']
                    attached_policy_name = attached_policy['PolicyName']
                    #uncomment the line below for troubleshooting
                    #print attached_policy_arn
                    #the exceptions below should be removed once the IAM policies are tightened
                    if not attached_policy_name.endswith("nfs-server-s3-policy"):
                        if ("stackstorm" and "server-elb-policy") not in attached_policy_name:
                            if ("stackstorm" and "server-s3-policy") not in attached_policy_name:
                                policy = client.get_policy(PolicyArn = attached_policy_arn)
                                policy_version = client.get_policy_version(PolicyArn = attached_policy_arn,VersionId = policy['Policy']['DefaultVersionId'])
                                #uncomment the line below for troubleshooting
                                #print(json.dumps(policy_version['PolicyVersion']['Document']['Statement']))
                                attached_policy_statement = json.dumps(policy_version['PolicyVersion']['Document']['Statement'])
                                if ':*' in attached_policy_statement:
                                    print ('IAM attached policy containing action wildcard:')
                                    print attached_policy_name
                                    wildcard_count +=1
        assert wildcard_count == 0   # Action wildcards must not be used in IAM policies

    def testInlinePolicyWildcards(self):
        region = os.environ["REGION"]
        client = boto3.client('iam', region_name=region)
        env = os.environ["ENVIRONMENT"]
        wildcard_count = 0
        for role in client.list_roles(MaxItems=1000)['Roles']:
            if role['RoleName'].startswith(env + '-') or role['RoleName'].startswith('etcd-' + env):
                role_name = role['RoleName']
                #uncomment the line below for troubleshooting
                #print role_name
                for inline_policy_name in client.list_role_policies(RoleName=role_name)['PolicyNames']:
                    #uncomment the line below for troubleshooting
                    #print inline_policy_name
                    inline_policy = client.get_role_policy(RoleName=role_name,PolicyName=inline_policy_name)
                    inline_policy_statement = json.dumps(inline_policy)
                    #uncomment the line below for troubleshooting
                    #print inline_policy_statement
                    if ':*' in inline_policy_statement:
                        print ('IAM inline policy containing action wildcard:')
                        print inline_policy_name
                        wildcard_count +=1
        assert wildcard_count == 0   # Action wildcards must not be used in IAM policies

if __name__ == '__main__':
    unittest.main()
