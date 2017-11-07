#!/bin/bash

print_pod_logs(){
  successPods=$(kubectl get pods --namespace=test-runner -l 'app in (testexecutor)' --show-all | grep Completed | awk '{print $1}')
  allPods=$(kubectl get pods --namespace=test-runner -l 'app in (testexecutor)' --show-all | awk '{print $1}' | tail -n +2)
  allPodCount=$(echo $allPods| wc -w)
  successfulPodCount=$(echo $successPods| wc -w)

  if [ -z $successfulPodCount ]; then
    successfulPodCount=0;
  fi

  echo
  echo "********************************************************************************************"
  echo "--------------------------------------------------------------------------------------------"
  echo "----------    Total Number of Pods Executed By Job         =  ${allPodCount}                "
  echo "----------    Number of Pods With Successful Tests         =  ${successfulPodCount}         "
  echo "--------------------------------------------------------------------------------------------"
  echo "********************************************************************************************"
  echo

  if [[ $allPodCount -eq 1 ]]; then  #If there is one pod, get logs for it
    lastPod=$(kubectl get pods --namespace=test-runner --show-all -o=custom-columns=STATUS:.status.startTime,NAME:.metadata.name,CONTAINER_STATUS:.status.containerStatuses  | grep testexecutor | sort | tail -n 1 | awk '{print $2}')
    echo
    echo "------------------------------------------------------------------------"
    echo "---------- Test Output From Pod:  ${lastPod} ---------------"
    echo "------------------------------------------------------------------------"
    echo
    kubectl logs $lastPod --namespace=test-runner

  else  #Get logs for next to last pod that ran. Don't get the last one as it might have been terminated by the kubernetes-tests job due to timeout
    nextToLastPod=$(kubectl get pods --namespace=test-runner --show-all -o=custom-columns=STATUS:.status.startTime,NAME:.metadata.name,CONTAINER_STATUS:.status.containerStatuses  | grep testexecutor | sort -r | head -n 3 | tail -n 1 | awk '{print $2}')
    echo
    echo "------------------------------------------------------------------------"
    echo "----------    Test Output From Pod :  ${nextToLastPod} -----------------"
    echo "------------------------------------------------------------------------"
    echo
    kubectl logs $nextToLastPod --namespace=test-runner
  fi

}

run_test(){
  kubectl get namespace test-runner > /dev/null 2>&1 || kubectl create namespace test-runner
  if $args; then
    cp job-withargs.yaml job-temp.yaml
    sed -i '' -e "s/%%TYPE%%/$TYPE/" job-temp.yaml > /dev/null 2>&1
    sed -i '' -e "s/%%FILES%%/$FILES/" job-temp.yaml > /dev/null 2>&1
  else
    cp job.yaml job-temp.yaml
  fi
  sed -i '' -e "s/%%TIMEOUT%%/$TIMEOUT/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%ENVIRONMENT%%/$ENVIRONMENT/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%BRAIN%%/$BRAIN/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%REGION%%/$REGION/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%STACK_ID%%/$STACK_ID/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%COMPLETIONS%%/$COMPLETIONS/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%PARRALLELISM%%/$PARRALLELISM/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%GIT_BRANCH%%/$GIT_BRANCH/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%DEBUG%%/$DEBUG/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%KUBE_PASS%%/$KUBE_PASS/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%KUBERNETES_VERSION%%/$KUBERNETES_VERSION/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%MINION_COUNT%%/$MINION_COUNT/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%ANSIBLE_BRANCH%%/$ANSIBLE_BRANCH/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%DOMAIN%%/$DOMAIN/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%CONSUL_MASTER_TOKEN%%/$CONSUL_MASTER_TOKEN/" job-temp.yaml > /dev/null 2>&1
  sed -i '' -e "s/%%ST2_PASSWORD%%/$ST2_PASSWORD/" job-temp.yaml > /dev/null 2>&1
  
  #Need to delete jobs
  if  [[ $(kubectl get jobs testexecutor --namespace=test-runner) ]]
  then  #Job already exists. Clean-up first
    kubectl delete jobs testexecutor --namespace=test-runner > /dev/null 2>&1
    kubectl create -f job-temp.yaml
  else
    kubectl create -f job-temp.yaml
  fi

  count=0
  while [ -n "$(kubectl get jobs testexecutor --namespace=test-runner --output json | jq '.status.conditions[].type' 2>&1 > /dev/null)" ]; do
     if [[ "$count" -gt $TIMEOUT ]]; then
       echo "Timed out waiting for Test Job to Complete. ${TIMEOUT} seconds have elapsed."
       print_pod_logs
       exit 1
     fi
     echo "Waiting on Test Job completion. ${count} seconds of ${TIMEOUT} second timeout have elapsed."
     sleep 30
     count=$((count+30))
  done
  if [[ "$(kubectl get jobs testexecutor --namespace=test-runner --output json | jq '.status.conditions[].type' | sed -e 's/\"//g')" = "Complete" ]]; then
    echo "Job Finshed Successfully, Retrieving Logs"
    sleep 30  #Wait a short bit before grabbing logs
    print_pod_logs
  elif [[ "$(kubectl get jobs testexecutor --namespace=test-runner --output json | jq '.status.conditions[].type' | sed -e 's/\"//g')" = "Failed" ]]; then
    echo "Job Finshed With Errors, Retrieving Logs"
    sleep 30  #Wait a short bit before grabbing logs
    print_pod_logs
    exit 1
  fi
}
display_usage() {
	echo -e "\nUsage:\n$0 -t <all|python|bats|inspec> -p <# pods> -c <# completions> -b <branch> -e <timeout> -f <file1> -f <file2> -f <filen> -d TRUE|FALSE"
  echo
  echo -e "Available Commands:\n"
  echo -e "   -t             (Required) Specifies the type of tests to execute. Allowed parameters are all, python, bats, or inspec"
  echo -e "                  Arguments:"
  echo -e "                      all: Execute all tests (bats/inspec/python) from the kubernetes-tests repository"
  echo -e "                      python: Execute 1-n python tests from kubernetes-tests/python_tests. The -f option"
  echo -e "                              is required when using the python arugument. Tests should be specified without the .py extension"
  echo -e "                      bats: Execute 1-n bats tests from kubernetes-tests/bats_tests. The -f option is required when using the bats argument"
  echo -e "                      inspec: Execute 1-n inspec tests from kubernetes-tests/inspec_tests that are part of the"
  echo -e "                              kubernetes-testss/inspec_tests/config.yaml. The -f option is required when using the inspec argument"
  echo -e "   -p              Specify parrallelism of test job.  How many pods to achieve success. Defaults to 1 if not specified"
  echo -e "   -c              Specify completions of test job.  How many successful completions of the tests are required to achieve success. Defaults to 1"
  echo -e "   -b              Specify the kubernetes-tests  branch to execute tests from.  Defaults to the dev branch"
  echo -e "   -e              Kill the job after a specified timeout in seconds if the job has not succeeded. Kubernetes will continue to"
  echo -e "                        spawn pods and try to get successful completion until the timeout is reached. Defaults to 120 seconds "
  echo -e "   -f              Specifies a test file to include in the test. This option may be specified multiple times to include multiple files."
  echo -e "   -d              Specify TRUE|FALSE for Debug mode. When in debug mode, the test job/pod will be started but will not shutdown so you may get into the pod to troubleshoot."
  echo
  exit 1
}


while getopts ":t:p:b:c:e:f:d:" o; do
    case "${o}" in
        t)
            t=${OPTARG}
            ;;
        p)
            p=${OPTARG}
            ;;
        b)
            b=${OPTARG}
            ;;
        c)
            c=${OPTARG}
            ;;
        e)
            e=${OPTARG}
            ;;
        f)
            multi+=("$OPTARG")
            ;;
        d)
            d=${OPTARG}
            ;;
        *)
            display_usage
            ;;
    esac
done
shift $((OPTIND-1))

args=false
#Build list of files if -f was specified
for val in "${multi[@]}"; do
  f=$val" "$f
done
if [[ "${t}" != "all" &&  "${t}" != "python" && "${t}" != "bats" && "${t}" != "inspec" ]]; then
    echo "Error: type (-t) argument must be specified"
    display_usage
fi

#Verify if all was not used, then files were provided
if [[ ("${t}" == "python" || "${t}" == "bats" || "${t}" == "inspec" ) && -z "${multi}" ]]; then
   echo "Error: The -f option must be specified when using the 'python|bats|inspec' test type (-t)"
   display_usage
fi

export TYPE=$t
export FILES=$f
export PARRALLELISM=$p
export GIT_BRANCH=$b
export COMPLETIONS=$c
export TIMEOUT=$e
export DEBUG=`echo ${d} | tr [a-z] [A-Z]`

#If type all was specified do not pass any file arguments on to the job
if [[ "${TYPE}"  == "all" ]]; then
  args=false
else
  args=true
fi

#Default timeout if not provided
if [[ -z "${e}" ]]; then
  export TIMEOUT=120
fi

#Default debug mode if not provided
if [[ -z "${d}" ]]; then
  export DEBUG=FALSE
fi

#Default parrallelism if not provided
if [[ -z "${p}" ]]; then
  export PARRALLELISM=1
fi

#Default branch if not provided
if [[ -z "${b}" ]]; then
  export GIT_BRANCH=dev
fi

#Default completions if not provided
if [[ -z "${c}" ]]; then
  export COMPLETIONS=1
fi

if [[ ( -z "$ENVIRONMENT") || ( -z "$REGION") || ( -z "$STACK_ID") ]]
then
   echo -e "Environment variables 'ENVIRONMENT', 'REGION', 'STACK_ID' not set"
   exit 1
fi
##Need to make a check for running this as root so there is access to Master ENV variables

run_test $args
