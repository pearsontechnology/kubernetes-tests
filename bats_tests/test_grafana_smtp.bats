#!/usr/bin/env bats

set -o pipefail

load helpers


@test "grafana smtp" {
    curl -k --user admin:${KUBE_PASS} -H "Content-Type: application/json" "https://grafana.default.svc.cluster.local:3000/api/alert-notifications/test" -d '{"name":"Grafana-test-email","type":"email","settings":{"addresses":"cloudops@pearson.com"}}'

}

