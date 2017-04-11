#!/bin/bash

while getopts ":d:" o; do
    case "${o}" in
        d)
            d=${OPTARG}
            ;;
    esac
done
shift $((OPTIND-1))

export DEBUG=`echo ${d} | tr [a-z] [A-Z]`
#Default debug mode if not provided
if [[ -z "${d}" ]]; then
  export DEBUG=FALSE
fi

kubectl get namespace test-runner > /dev/null 2>&1 || kubectl create namespace test-runner

cp pod.yaml pod-temp.yaml

sed -i '' -e "s/%%STACK_ID%%/$STACK_ID/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%ANSIBLE_BRANCH%%/$ANSIBLE_BRANCH/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%REGION%%/$REGION/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%ENVIRONMENT%%/$ENVIRONMENT/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%GIT_BRANCH%%/$TEST_BRANCH/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%KUBE_PASS%%/$KUBE_PASS/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%MINION_COUNT%%/$MINION_COUNT/" pod-temp.yaml > /dev/null 2>&1
sed -i '' -e "s/%%DEBUG%%/$DEBUG/" pod-temp.yaml > /dev/null 2>&1

if  [[ $(kubectl get rc testexecutor --namespace=test-runner) ]]
then  #RC already exists. Clean-up first
  kubectl delete rc testexecutor --namespace=test-runner > /dev/null 2>&1
  kubectl create -f pod-temp.yaml
else
  kubectl create -f pod-temp.yaml
fi


kubectl create -f pod-temp.yaml
