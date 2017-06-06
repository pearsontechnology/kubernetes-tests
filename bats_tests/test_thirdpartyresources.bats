#!/usr/bin/env bats

set -o pipefail

load helpers

@test "grafana thirdpartyresource" {
  kubectl get thirdpartyresources ${ENVIRONMENT}-grafana.prsn.io --namespace=default --no-headers
}

@test "mongo thirdpartyresource" {
  kubectl get thirdpartyresources mongo.prsn.io --namespace=default --no-headers
}

@test "mysql thirdpartyresource" {
  kubectl get thirdpartyresources mysql.prsn.io --namespace=default --no-headers
}
