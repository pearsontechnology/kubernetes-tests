# kubernetes-tests

Kubernetes (k8s) containerized/deployable test suite.  This repo allows the execution of BATS, INSPEC, and Python tests against a deployed PaaS.  Through the usage of kubernetes jobs a test contianer spins up execute a specified number of tests against the nodes within the kubernetes PaaS.  

==========================================================================================

**Building a new version of the [test container docker image](https://hub.docker.com/r/pearsontechnology/test-executor-app)**

1) Clone the kubernetes-tests repository

```git clone -q -b <your branch> git@github.com:pearsontechnology/kubernetes-tests.git```

2) Build a new Docker

```
cd kuberenets-tests/test-executor-app
export VERSION=<MAJOR>.<MINOR>.<PATCH>
```
Note: [Current Docker Image Versions](https://hub.docker.com/r/pearsontechnology/test-executor-app/tags/)
```
docker build -t pearsontechnology/test-executor-app:${VERSION} .
```
3)  Push the new Docker to DockerHub
```
docker login  #Provide DockerHub Credentials
docker push pearsontechnology/test-executor-app:1.0.0
```
4)  Update Yaml files that utilize the new Docker image version:

 - [job.yaml](./job.yaml)  
 - [job-withargs.yaml](./job-withargs.yaml)
 - [pod.yaml](./pod.yaml)

**Overview of Run Scripts**

1) Familiarize yourself with some of the files that are used to start the kubernetes jobs:

- [run-containerized-tests.sh](./run-containerized-tests.sh) - This file configures a kubernetes job v,  runs the job, monitors progress, and then reports results from completed or error pod logs that were part of the job.
- [execute-test-pod.sh](./execute-test-pod.sh) - This file runs the test-executor-app docker image in a kubernetes pod and follows the pod logs after it starts so you may monitor test execution.
- [run.sh](./test-executor-app/run.sh) - This is the test container Docker entry point. It builds up a hosts.yaml file for a list of hosts that will be under tests in the cluster, configures kubectl, and then starts the tests by launching testRunner.py
- [testRunner.py](./test-executor-app/testRunnery.py) - This file is built into the test container image and is responsible for execution of the INSPEC/BATS/Python tests in the kubernetes-tests repo.

==========================================================================================

**Test Execution Options/Examples for Running a Job:**

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

**Test Execution Options/Examples for Running a Pod:**

Example1: Execute all tests against your deployment in a pod for dev branch of kubernetes-tests

```
     ./execute-test-pod.sh -d FALSE -b dev
```

**Available Options: execute-test-pod.sh**

Execute  ./execute-test-pod.sh  without any arguments to get command help

```
Overall Usage: ./execute-test-pod.sh -d <TRUE/FALSE> -b <kuberenets-test branch>
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
