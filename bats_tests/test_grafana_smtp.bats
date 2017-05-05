#!/usr/bin/env bats

set -o pipefail

load helpers


@test "grafana smtp" {
    curl -k --user admin:${KUBE_PASS} -H "Content-Type: application/json" "https://grafana-${ENVIRONMENT}.prsn.io/api/alert-notifications/test" -d '{"name":"Grafana-test-email","type":"email","settings":{"addresses":"cloudops@pearson.com"}}'

}

