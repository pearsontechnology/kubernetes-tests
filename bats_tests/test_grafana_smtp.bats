#!/usr/bin/env bats

set -o pipefail

load helpers


@test "grafana smtp" {
    # curl -k --user admin:${KUBE_PASS} -H "Content-Type: application/json" "http://grafana.default.svc.cluster.local:3000/api/alert-notifications/test" -d '{"name":"Grafana-test-email","type":"email","settings":{"addresses":"cloudops@pearson.com"}}' | grep "Test notification sent" 
    curl -k --user admin:${KUBE_PASS} -H "Content-Type: application/json" "http://grafana.default.svc.cluster.local:3000/api/alert-notifications/test" -d '{"name":"Grafana-test-email","type":"email","settings":{"addresses":"thilina.piyasundara@pearson.com"}}' | grep "Test notification sent" 

}

