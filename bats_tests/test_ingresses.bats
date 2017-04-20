#!/usr/bin/env bats

set -o pipefail

load helpers

# Ingress

@test "grafana ingress" {
  kubectl get ing grafana --namespace=default --no-headers
}

@test "ingress without host defined does not generate" {
  assets_folder="/tmp/kubernetes-tests/test_assets"
  run kubectl get ing --namespace=kube-system ingress-host-test --no-headers
  if [ "$status" -eq 0 ]; then
    if [ "$output" != "" ]; then
      kubectl delete -f $assets_folder/ingress.hashost.yaml
    fi
  fi
  kubectl create -f $assets_folder/ingress.hashost.yaml
  sleep 10
  pods="$(kubectl get pods --namespace=kube-system | grep -oEi 'nginx-ingress-[0-9a-z]+')"
  run filtered_ingress_logs_eq_0 $pods "ingress-host-test"
  kubectl delete -f $assets_folder/ingress.hashost.yaml
  kubectl create -f $assets_folder/ingress.nohost.yaml
  sleep 10
  pods="$(kubectl get pods --namespace=kube-system | grep -oEi 'nginx-ingress-[0-9a-z]+')"
  run filtered_ingress_logs_gt_0 $pods "ingress-host-test"
  kubectl delete -f $assets_folder/ingress.nohost.yaml
}

#@test "es ingress" {
#  kubectl get ing es-ingress --namespace=default --no-headers
#}
