# Python tests

This repository contains tests for bitesize environments. Tests are divided into test groups (bats tests, inspec tests, python tests) and targets (stackstorm, kubernetes, consul, etc.).

## Running stackstorm tests

Tests can be run individually or as a full test suite. All stackstorm tests need the following environment variables set:

* *ST2_ADDRESS* - stackstorm host to execute tests against. Can be stackstorm instance IP (can be found with `bitesize-cluster-endpoints.py`) or load balancer IP.
* *ST2_APIKEY* - API key to communicate with stackstorm instance. If you don't have one, you can create it by running `st2 apikey create` on stackstorm instance, and setting environment variable to `key` value.

#### Running all tests

```
$ ST2_ADDRESS=x.x.x.x ST2_APIKEY=yyy nose2 -v -s stackstorm
```

#### Running individual suite

```
$ ST2_ADDRESS=x.x.x.x ST2_APIKEY=yyyy python stackstorm/test_bitesize_pack.py
```

#### Running individual test

```
$ ST2_ADDRESS=x.x.x.x ST2_APIKEY=yyyy python stackstorm/test_bitesize_pack.py BitesizePack.test_create_ns
```
