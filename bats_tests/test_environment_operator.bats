#!/usr/bin/env bats

set -o pipefail

load helpers


@test "environment operator deploy of hello world test app" {
  assets_folder="/tmp/kubernetes-tests/test_assets"

  #Clean up namespace from previous test executions
  run kubectl get namespace nodejs-hello-world-app
  if [ "$status" -eq 0 ]; then
    kubectl delete namespace nodejs-hello-world-app  
  fi
  while true; do
    run kubectl get namespace nodejs-hello-world-app
    if [ "$status" -eq 0 ]; then
      sleep 2
    else
      break;
    fi
  done

  #Deploy Environment Operator for nodejs-hello-world-app
  kubectl create namespace nodejs-hello-world-app
  cp /etc/secret-volume/git-key ./key
  export AUTH_TOKEN=`cat /etc/secret-volume/token`
  kubectl get secret git-private-key --namespace=nodejs-hello-world-app > /dev/null 2>&1 || kubectl create secret generic git-private-key --from-file=./key --namespace=nodejs-hello-world-app
  kubectl get secret auth-token-file --namespace=nodejs-hello-world-app > /dev/null 2>&1 || kubectl create secret generic auth-token-file --from-file=/etc/secret-volume/token --namespace=nodejs-hello-world-app
  kubectl create -f $assets_folder/environment-operator.yaml --namespace=nodejs-hello-world-app
  kubectl create -f $assets_folder/environment-operator-ing.yaml --namespace=nodejs-hello-world-app 
  kubectl create -f $assets_folder/environment-operator-svc.yaml --namespace=nodejs-hello-world-app 

  sleep 10 

  curl -k -XPOST -H "Authentication: Bearer $AUTH_TOKEN" -H 'Content-Type: application/json' -d '{"application":"front", "name":"front", "version":"1.0.1"}' environment-operator.nodejs-hello-world-app.prsn-dev.io/deploy

}
