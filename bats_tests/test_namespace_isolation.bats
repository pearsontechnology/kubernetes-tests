#!/usr/bin/env bats

set -o pipefail

# Services

@test "Verify Namespace Cannot Access K8s API in Different Namespace" {
    export KUBE_TOKEN=`cat /var/run/secrets/kubernetes.io/serviceaccount/token`
    curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/kube-system/pods | grep Forbidden
}

@test "Verify Kubernetes API can be reached from the same Namespace" {
    export KUBE_TOKEN=`cat /var/run/secrets/kubernetes.io/serviceaccount/token`
    curl -sSk -H "Authorization: Bearer $KUBE_TOKEN" https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_PORT_443_TCP_PORT/api/v1/namespaces/test-runner/pods | grep testexecutor
}
