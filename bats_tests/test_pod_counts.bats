#!/usr/bin/env bats

set -o pipefail

load helpers

@test "bitesize-registry pods" {
  BITESIZE_REGISTRY_DESIRED=`kubectl get rc bitesize-registry --namespace=default -o jsonpath='{.spec.replicas}'`
  BITESIZE_REGISTRY_CURRENT=`kubectl get rc bitesize-registry --namespace=default -o jsonpath='{.status.replicas}'`
  values_equal $BITESIZE_REGISTRY_DESIRED $BITESIZE_REGISTRY_CURRENT
}

@test "kube-dns pods" {
  KUBE_DNS_DESIRED=`kubectl get rc kube-dns-v18 --namespace=kube-system -o jsonpath='{.spec.replicas}'`
  KUBE_DNS_CURRENT=`kubectl get rc kube-dns-v18 --namespace=kube-system -o jsonpath='{.status.replicas}'`
  values_equal $KUBE_DNS_DESIRED $KUBE_DNS_CURRENT
}

# @test "es-master pods" {
#   ES_MASTER_DESIRED=`kubectl get deployments es-master --namespace=default -o jsonpath='{.spec.replicas}'`
#   ES_MASTER_CURRENT=`kubectl get deployments es-master --namespace=default -o jsonpath='{.status.replicas}'`
#   values_equal $ES_MASTER_DESIRED $ES_MASTER_CURRENT
# }
#
# @test "es-data pods" {
#   ES_DATA_DESIRED=`kubectl get deployments es-data --namespace=default -o jsonpath='{.spec.replicas}'`
#   ES_DATA_CURRENT=`kubectl get deployments es-data --namespace=default -o jsonpath='{.status.replicas}'`
#   values_equal $ES_DATA_DESIRED $ES_DATA_CURRENT
# }
#
# @test "es-client pods" {
#   ES_CLIENT_DESIRED=`kubectl get deployments es-client --namespace=default -o jsonpath='{.spec.replicas}'`
#   ES_CLIENT_CURRENT=`kubectl get deployments es-client --namespace=default -o jsonpath='{.status.replicas}'`
#   values_equal $ES_CLIENT_DESIRED $ES_CLIENT_CURRENT
# }

@test "heapster-v1.2.0.1 pods" {
  HEAPSTER_DESIRED=`kubectl get deployments heapster-v1.2.0.1 --namespace=kube-system -o jsonpath='{.spec.replicas}'`
  HEAPSTER_CURRENT=`kubectl get deployments heapster-v1.2.0.1 --namespace=kube-system -o jsonpath='{.status.replicas}'`
  values_equal $HEAPSTER_DESIRED $HEAPSTER_CURRENT
}

@test "grafana pods" {
  GRAFANA_DESIRED=`kubectl get rc grafana --namespace=default -o jsonpath='{.spec.replicas}'`
  GRAFANA_CURRENT=`kubectl get rc grafana --namespace=default -o jsonpath='{.status.replicas}'`
  values_equal $GRAFANA_DESIRED $GRAFANA_CURRENT
}

@test "keycloak pods" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi

  KEYCLOAK_DESIRED=`kubectl get deployment kc --namespace=keycloak -o jsonpath='{.spec.replicas}'`
  KEYCLOAK_CURRENT=`kubectl get deployment kc --namespace=keycloak -o jsonpath='{.status.replicas}'`
  values_equal $KEYCLOAK_DESIRED $KEYCLOAK_CURRENT
}
