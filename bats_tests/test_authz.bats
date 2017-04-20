#!/usr/bin/env bats

set -o pipefail

load helpers

@test "Test Authz service account access for namespaces" {
  assets_folder="/tmp/kubernetes-tests/test_assets"
  kubectl create ns test-namespace-dev
  kubectl create ns test-namespace-prd
  kubectl create ns test-namespace-qa

  run kubectl get pod --namespace=test-namespace-dev simple-pod --no-headers
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete -f $assets_folder/simple-pod.yaml
    fi
  fi
  kubectl create -f $assets_folder/simple-pod.yaml
  sleep 10

  kubectl exec simple-pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-dev
  kubectl exec simple-pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-qa
  kubectl exec simple-pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-prd

  kubectl delete -f $assets_folder/simple-pod.yaml
  kubectl delete ns test-namespace-dev
  kubectl delete ns test-namespace-prd
  kubectl delete ns test-namespace-qa
}
