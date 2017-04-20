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

  kubectl create ns test-namespace-dev
  kubectl create ns test-namespace-prd
  kubectl create ns test-namespace-qa

  run kubectl get deployment --namespace=test-namespace-dev jenkins --no-headers
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete -f $assets_folder/jenkins-dep.yaml
    fi
  fi
  kubectl create -f $assets_folder/jenkins-dep.yaml
  sleep 20
  pod="$(kubectl get pods --namespace=test-namespace-dev | grep -oEi 'jenkins-[0-9a-z]+-[0-9a-z]+')"

  kubectl exec $pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-dev
  kubectl exec $pod --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-qa
  kubectl exec $pod  --namespace=test-namespace-dev -- kubectl get pods --namespace=test-namespace-prd

  kubectl delete -f $assets_folder/jenkins-dep.yaml
  kubectl delete ns test-namespace-dev
  kubectl delete ns test-namespace-prd
  kubectl delete ns test-namespace-qa
}
