#!/usr/bin/env bats

set -o pipefail

load helpers

@test "Test Authz service account access for namespaces" {
  assets_folder="/tmp/kubernetes-tests/test_assets"


  run kubectl get ns test-namespace-dev
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete ns test-namespace-dev
    fi
  fi

  run kubectl get ns test-namespace-prd
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete ns test-namespace-prd
    fi
  fi

  run kubectl get ns test-namespace-qa
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete ns test-namespace-qa
    fi
  fi

  #Wait for NS deletion (2 min max wait for command to come back non-zero)
  wait-for-nonzero-code "kubectl get ns test-namespace-prd > /dev/null"
  wait-for-nonzero-code "kubectl get ns test-namespace-stg > /dev/null"
  wait-for-nonzero-code "kubectl get ns test-namespace-dev > /dev/null"

  kubectl create ns test-namespace-dev
  kubectl create ns test-namespace-prd
  kubectl create ns test-namespace-qa

  kubectl create -f $assets_folder/jenkins-dep.yaml

  #Wait for jenkins pod creation (2 min max wait for command to come back with zero exit code)
  wait-for-success "kubectl get pods --namespace=test-namespace-dev $pod | grep -i jenkins | awk '{print $3}' | grep -i Running > dev/null"

  kubectl exec $pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-dev
  kubectl exec $pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-qa
  kubectl exec $pod  --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-prd

  kubectl delete -f $assets_folder/jenkins-dep.yaml
  kubectl delete ns test-namespace-dev
  kubectl delete ns test-namespace-prd
  kubectl delete ns test-namespace-qa
}
