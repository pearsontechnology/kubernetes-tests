#!/usr/bin/env bats

set -o pipefail

load helpers

# User pods

@test "bitesize-registry" {
  kubectl get pods --namespace=default --no-headers | grep bitesize-registry | grep Running
}

# @test "es-master" {
#   kubectl get pods --namespace=default --no-headers | grep es-master | grep Running
# }
#
# @test "es-data" {
#   kubectl get pods --namespace=default --no-headers | grep es-data | grep Running
# }
#
# @test "es-client" {
#   kubectl get pods --namespace=default --no-headers | grep es-client | grep Running
# }

@test "kube-dns" {
  kubectl get pods --namespace=kube-system --no-headers | grep kube-dns | grep Running
}

@test "monitoring-heapster-v6" {
  kubectl get pods --namespace=kube-system --no-headers | grep monitoring-heapster-v6 | grep Running
}

@test "consul" {
  kubectl get pods --namespace=kube-system --no-headers | grep consul | grep Running
}

@test "vault" {
  kubectl get pods --namespace=kube-system --no-headers | grep vault | grep Running
}

# # Test Elasticsearch cluster is up and green
# @test "elasticsearch-default-svc-cluster-local" {
#   curl --connect-timeout 30 --max-time 60 http://elasticsearch.default.svc.cluster.local:9200/_cluster/health | grep status | grep green
# }

@test "td-agent-es" {
  kubectl get pods --namespace=kube-system --no-headers | grep td-agent-es | grep Running
}

@test "sysdig-agent" {
  kubectl get pods --namespace=kube-system --no-headers | grep sysdig-agent | grep Running
}

@test "pod-authentication-with-K8S-API" {
  curl -k -N -X GET -u admin:${KUBE_PASS} https://$KUBERNETES_SERVICE_HOST:443/api/v1/
}
