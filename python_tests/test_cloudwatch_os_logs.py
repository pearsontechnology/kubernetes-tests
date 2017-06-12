#!/usr/bin/python
import boto3
import os

##Verify cloudwatch log groups exist for audit and syslog
def test_cloudwatch_os_log_groups_exist():
    logs = boto3.client('logs', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    log_group_count = 0
    log_groups = logs.describe_log_groups()
    for log in log_groups ['logGroups']:
        if (env in log['logGroupName']) and log['logGroupName'].startswith("/bitesize"):
            if log['logGroupName'].endswith("/audit"):
                log_group_count += 1
            if log['logGroupName'].endswith("/syslog"):
                log_group_count += 1
        assert log_group_count == 4   #should be a total of 4 Cloudwatch audit and syslog log groups

test_cloudwatch_os_log_groups_exist()
