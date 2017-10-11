#!/usr/bin/env bats

set -o pipefail

load helpers

# Infrastructure

@test "master" {
  kubectl get nodes --no-headers --selector=role=master | grep " Ready"
}

@test "minion" {
  kubectl get nodes --no-headers --selector=role=minion | grep " Ready"
}

@test "loadbalancer" {
  kubectl get nodes --no-headers --selector=role=loadbalancer | grep " Ready"
}
