## Kubernetes Testing

This repository is the containerized/deployable test suite that may be utilized to validate a kubernetes deployment.  This repo allows the execution of BATS, INSPEC, and Python tests against a deployed PaaS.  Through the usage of kubernetes jobs/pods a test container spins up execute a specified number of tests against the nodes within the kubernetes PaaS.  

==========================================================================================

**Building a new version of the [test container docker image](https://hub.docker.com/r/pearsontechnology/test-executor-app)**

1) Clone the kubernetes-tests repository and create your own branch

```
git clone -q -b dev git@github.com:pearsontechnology/kubernetes-tests.git
git checkout -b [name_of_your_new_branch]
git push -u origin [name_of_your_new_branch]
```

2) Build a new Docker

```
cd kuberenets-tests/test-executor-app
export VERSION=<MAJOR>.<MINOR>.<PATCH>
```

 -  Note: Review current [Image Versions](https://hub.docker.com/r/pearsontechnology/test-executor-app/tags/) when picking your new version.
```
docker build -t pearsontechnology/test-executor-app:${VERSION} .
```
3)  Push the new Docker image to DockerHub
```
docker login  #Provide DockerHub Credentials
docker push pearsontechnology/test-executor-app:1.0.0
```
4)  Update Yaml Files that utilize the new Docker image version in your branch. Below are the files as they are in the dev branch:

 - [job.yaml](https://github.com/pearsontechnology/kubernetes-tests/blob/master/job.yaml)
 - [job-withargs.yaml](https://github.com/pearsontechnology/kubernetes-tests/blob/master/job-withargs.yaml)
 - [pod.yaml](https://github.com/pearsontechnology/kubernetes-tests/blob/master/pod.yaml)


**Overview of scripts within kubernetes-tests**

Familiarize yourself with some of the files that are used to start the kubernetes jobs:

- [execute-test-pod.sh](./execute-test-pod.sh) - This file runs the test-executor-app docker image in a kubernetes pod and follows the pod logs after it starts so you may monitor test execution. This should be used by the Bitesize team to run/develop tests for a deployment.
- [run-containerized-tests.sh](./run-containerized-tests.sh) - This file configures the kubernetes job via available options,  runs the job, monitors progress, and then reports results from completed or error pod logs that were part of the job.  Travis CI utilizes this script by call it from the [run-tests.sh](https://github.com/pearsontechnology/bitesize/blob/dev/test/kubernetes/run-tests.sh) script that gets put on the Master instance in the PaaS
- [run.sh](./test-executor-app/run.sh) - This is the test container Docker entry point. It builds up a hosts.yaml file for a list of hosts that will be under tests in the cluster, configures kubectl, and then starts the tests by launching testRunner.py
- [testRunner.py](./test-executor-app/testRunnery.py) - This file is built into the test container image and is responsible for execution of the INSPEC/BATS/Python tests in the kubernetes-tests repo.


==========================================================================================
<a id="Environment"></a>

**What's Required By the Test Container to Run in Kubernetes?**

The test container requires secrets to be set to enable ssh'ing into other nodes in the cluster as well as to interact with Git. Below is an overview of these secrets which need to exist in the test-runner namespace priot to executing the test container.

- **bitesize.key** :  This is the key used to ssh from yor master kubernetes node to other nodes in the private subnet
- **kubectl-client-key** : This is the client key used by kubectl which will be used in the container to setup kubectl config
- **kubectl-ca** : This is the certificate authority used by kubectl which will be used in the container to setup kubectl config
- **jenkins-user and jenkins-pass** : These username/passwords are used by the [jenkins-dep.yaml](./test-executor-app/jenkins-dep.yaml), [jenkins-svc.yaml](./test-executor-app/jenkins-svc.yaml), [jenkins-ing.yaml](./test-executor-app/jenkins-ing.yaml)  files to build a new test container image. The jenkins image and jenkins plugin are not yet opensourced.
- **git-username/password** : Used by the container to access git and retrieve the kubernetes-tests repo for Execution. This is your git username and git access token.

```
kubectl get secrets test-runner-secrets --namespace=test-runner > /dev/null 2>&1 || kubectl create secret generic test-runner-secrets \
  --from-file=bitesize-priv-key=/root/.ssh/bitesize.key \
  --from-file=kubectl-client-key=/root/.ssh/bitesizessl.pem \
  --from-file=kubectl-ca=/root/.ssh/ca.pem \
  --from-file=git-key=/root/.ssh/git.key \
  --from-literal=jenkins-user=jenkins-user \
  --from-literal=jenkins-pass=jenkins-pass \
  --from-literal=git-username=username \
  --from-literal=git-password=git-token \
  --namespace=test-runner
```
==========================================================================================

**Test Execution Options/Examples for Running tests by a single Pod:**

Example1: Execute all tests against your deployment in a pod for dev branch of kubernetes-tests

```
     ./execute-test-pod.sh -d FALSE -b dev
```

**Available Options: execute-test-pod.sh**

Execute  ./execute-test-pod.sh  without any arguments to get command help and more information on options.

```
Overall Usage: ./execute-test-pod.sh -d <TRUE/FALSE> -b <kuberenets-test branch>
```
==========================================================================================

**Test Execution Options/Examples for Running a Job:**

Note: These are rarely used, but could be added to the [run-tests.sh](https://github.com/pearsontechnology/bitesize/blob/dev/test/kubernetes/run-tests.sh) script that gets executed by our master user-data.

Example1: Execute all tests (python/inspec/bats within kubernetes-tests) against your deployment

```
     ./run-containerized-tests.sh -t all
```
Example1: Execute all tests (python/inspec/bats within kubernetes-tests) against your deployment from a specific kubernetes-tests branch

```
     ./run-containerized-tests.sh -t all -b mybranch
```

Example2: Execute a bats test 100 times against your deployment using at most 5 pods in parrallel to reach the 100 desired completions

```
     ./run-containerized-tests.sh -t bats -f test_namespace_isolation.bats -c 100 -p 5
```

Example3: Execute a python test against your deployment

```
     ./run-containerized-tests.sh -t python -f test_namespace_isolation
```

     Note:  When specifying python tests, you omit the .py extension from your filename

Example4: Execute two inspec tests against your deployment

      Ensure your tests are listed under the instance type that they should be executed  against in <kubernetes-tests>/inspec_tests/config.yaml

```
     ./run-containerized-tests.sh -t inspec -f master_spec.rb -f minion_spec.rb
```


**Available Options: run-containerized-tests.sh**

Execute  ./run-containerized-tests.sh  without any arguments to get command help

```
Overall Usage: ./run-containerized-tests.sh -t <all|python|bats|inspec> -p <# pods> -c <# completions> -b <branch> -e <timeout> -f <file1> -f <file2> -f <filen>
```
==========================================================================================

**kubernetes-tests/inspec_tests/config.yaml**

This file is utilized by the test container within the [testRunnery.py](./test-executor-app/testRunnery.py) script to determine what INSPEC tests to run. Specifies  the server types and the associated INSPEC controls that should be executed against the given server type.  The test container job will evaluate this config file against the available server name tags in your deployment and will apply those control tests against your server.  Executing ./run-containerized-tests.sh -t all" with the config below in place would execute the two control tests against master and bastion instances in your deployment.  More information on how to write Chef Inspec tests may be found [here](https://docs.chef.io/inspec.html)

```
    master:
      - test_master_spec.rb
    etcd:
    nfs:
    loadbalancer:
    stackstorm:
    auth:
    minion:
    bastion:
      - test_bastion_spec.rb
```
