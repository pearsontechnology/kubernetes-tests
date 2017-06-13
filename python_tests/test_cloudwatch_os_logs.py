#!/usr/bin/python
import boto3
import sys
import os
import time
import json
import argparse

from botocore.exceptions import ClientError
from datetime import datetime

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

##Verify audit log streams written to Cloudwatch log groups
def test_cloudwatch_audit_log_streams():
    logs = boto3.client('logs', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    log_groups = logs.describe_log_groups()
    audit_log_stream_count = 0
    for log_group in log_groups ['logGroups']:
        if (env in log_group['logGroupName']) and log_group['logGroupName'].startswith("/bitesize") and log_group['logGroupName'].endswith("/audit"):
            log_stream_data = logs.describe_log_streams(logGroupName = log_group['logGroupName'])
            for log_stream in log_stream_data['logStreams']:
                if (log_stream['logStreamName'].startswith("10.") or log_stream['logStreamName'].startswith("172.")):
                    audit_log_stream_count +=1
    assert audit_log_stream_count >= 6   #should be at least 6 Cloudwatch audit log streams

##Verify syslog log streams written to Cloudwatch log groups
def test_cloudwatch_syslog_log_streams():
    logs = boto3.client('logs', region_name=os.environ["REGION"])
    env = os.environ["ENVIRONMENT"]
    log_groups = logs.describe_log_groups()
    syslog_log_stream_count = 0
    for log_group in log_groups ['logGroups']:
        if (env in log_group['logGroupName']) and log_group['logGroupName'].startswith("/bitesize") and log_group['logGroupName'].endswith("/syslog"):
            log_stream_data = logs.describe_log_streams(logGroupName = log_group['logGroupName'])
            for log_stream in log_stream_data['logStreams']:
                if (log_stream['logStreamName'].startswith("10.") or log_stream['logStreamName'].startswith("172.")):
                    syslog_log_stream_count +=1
    assert syslog_log_stream_count >= 6   #   #should be at least 6 Cloudwatch syslog log streams
