#!/usr/bin/env bats

set -o pipefail

load helpers

# Ingress

@test "vault ingress" {
  kubectl get ing vault --namespace=kube-system --no-headers
}

@test "grafana ingress" {
  kubectl get ing grafana --namespace=default --no-headers
}

#@test "es ingress" {
#  kubectl get ing es-ingress --namespace=default --no-headers
#}
