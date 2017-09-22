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
      kubectl delete -f $assets_folder/ingress.hashost.yaml --namespace=kube-system
    fi
  fi
  kubectl create -f $assets_folder/ingress.hashost.yaml --namespace=kube-system
  sleep 10
  pods="$(kubectl get pods --namespace=kube-system | grep -oEi 'nginx-ingress-[0-9a-z]+')"
  run filtered_ingress_conf_gt_0 $pods "ingress-host-test"
  kubectl delete -f $assets_folder/ingress.hashost.yaml --namespace=kube-system
  kubectl create -f $assets_folder/ingress.nohost.yaml --namespace=kube-system
  sleep 10
  pods="$(kubectl get pods --namespace=kube-system | grep -oEi 'nginx-ingress-[0-9a-z]+')"
  run filtered_ingress_conf_eq_0 $pods "ingress-host-test"
  run filtered_ingress_logs_gt_0 $pods "Ingress ingress-host-test failed validation: Host must be set"
  kubectl delete -f $assets_folder/ingress.nohost.yaml --namespace=kube-system
}


@test "keycloak ingress" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi
  kubectl get ing keycloak --namespace=keycloak --no-headers
}

#@test "es ingress" {
#  kubectl get ing es-ingress --namespace=default --no-headers
#}
