#!/bin/bash

if [[ ( -z "$ENVIRONMENT") || ( -z "$REGION") || ( -z "$STACK_ID") ]]
then
   echo -e "Environment variables 'ENVIRONMENT', 'REGION', 'STACK_ID' not set"
   exit 1
fi

cp pod.yaml pod-temp.yaml

sed -i '' -e "s/%%STACK_ID%%/$STACK_ID/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%ANSIBLE_BRANCH%%/$ANSIBLE_BRANCH/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%REGION%%/$REGION/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%ENVIRONMENT%%/$ENVIRONMENT/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%GIT_BRANCH%%/$TEST_BRANCH/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%KUBE_PASS%%/$KUBE_PASS/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%MINION_COUNT%%/$MINION_COUNT/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%DEBUG%%/$DEBUG/" pod-temp.yaml > /dev/null 2>&1

kubectl create -f pod-temp.yaml
