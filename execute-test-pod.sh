#!/bin/bash
display_usage() {
	echo -e "\nUsage:\n$0 -d <TRUE/FALSE> -b <kubernetes-test branch>"
  echo
  echo -e "Available Commands:\n"
  echo -e "   -d              REQUIRED: Specify TRUE|FALSE for Debug mode. When in debug mode, the test pod will be started but will not shutdown after tests complete. "
  echo -e "                             This provides the ability for developers to get into the pod and debug/develop tests."
  echo -e "   -b              REQUIRED: Specify kubernetes-test branch."
  echo -e "                             This is the branch that gets pulled into the test pod for execution against the kubernetes cluster"
  echo
  exit 1
}

while getopts ":d:b:" o; do
    case "${o}" in
        d)
            d=${OPTARG}
            ;;
        b)
            b=${OPTARG}
            ;;
    esac
done
shift $((OPTIND-1))

export DEBUG=`echo ${d} | tr [a-z] [A-Z]`
#Default debug mode if not provided
if [[ -z "${d}" ]]; then
  display_usage
fi

if [[ -z "${b}" ]]; then
  display_usage
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

if  [[ $(kubectl get pod testexecutor --namespace=test-runner) ]]
then
  kubectl delete -f pod-temp.yaml
  kubectl create -f pod-temp.yaml
else
  kubectl create -f pod-temp.yaml
fi

count=0
podstate=`kubectl get pods --namespace=test-runner | grep -i testexecutor | grep -i Running | awk '{print $3}'`
while [[ "$podstate" != "Running" ]];do
  if [ $count -gt 10 ]; then
    echo "Testexecutor pod did not enter a running state"
    exit 1
  fi
  echo "Waiting on Pod to begin running $(($count * 5))/$((10 * 5))"
  sleep 5
  podstate=`kubectl get pods --namespace=test-runner | grep -i testexecutor | grep -i Running | awk '{print $3}'`
  let count=count+1
done

kubectl logs -f testexecutor -c test-executor-app --namespace=test-runner
