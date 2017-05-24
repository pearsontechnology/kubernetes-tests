#!/usr/bin/env bats

set -o pipefail

load helpers


@test "k8s auth" {
    curl -k -N -X GET -u admin:${KUBE_PASS} https://$KUBERNETES_SERVICE_HOST:443/api/v1/

}

