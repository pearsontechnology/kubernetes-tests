#!/usr/bin/python
import boto3
import sys
import os
import time
import json
import argparse

from botocore.exceptions import ClientError
from datetime import datetime

##Verify cloudwatch log groups exist for flowlogs
def test_cloudwatch_flowlog_log_groups_exist():
    logs = boto3.client('logs', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    log_group_count = 0
    log_groups = logs.describe_log_groups(logGroupNamePrefix='/bitesize-' + env)
    for log in log_groups ['logGroups']:
        if log['logGroupName'].endswith("/flowlog"):
            log_group_count += 1
    assert log_group_count == 2   #should be a flowlog log group for the Bitesize VPC and another for the database VPC

##Verify flowlog log streams written to flowlog log group for Bitesize VPC
def test_cloudwatch_flowlog_log_streams():
    logs = boto3.client('logs', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    log_groups = logs.describe_log_groups(logGroupNamePrefix='/bitesize-' + env)
    syslog_log_stream_count = 0
    for log_group in log_groups ['logGroups']:
        if (log_group['logGroupName'].endswith("/flowlog")):
            log_stream_data = logs.describe_log_streams(logGroupName = log_group['logGroupName'])
            for log_stream in log_stream_data['logStreams']:
                if (log_stream['logStreamName'].startswith("eni")):
                    syslog_log_stream_count +=1
    assert syslog_log_stream_count >= 1   #   #should be at least 1 flowlog log stream
