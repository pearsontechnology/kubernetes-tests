#!/usr/bin/env bats

set -o pipefail

load helpers

@test "load kubetests-prd" {
  assets_folder="/tmp/kubernetes-tests/test_assets/migrate"
  run kubectl create ns kubetests-prd
  run kubectl create -f $assets_folder/deployment.yaml
  run kubectl create -f $assets_folder/limits.yaml
  run kubectl create -f $assets_folder/pv.yaml
  run kubectl create -f $assets_folder/pvc.yaml
  run kubectl create -f $assets_folder/quota.yaml
  run kubectl create -f $assets_folder/rc.yaml
  run kubectl create -f $assets_folder/secret.yaml
  run kubectl create -f $assets_folder/serviceaccount.yaml
  run kubectl create -f $assets_folder/tprtype.yaml
  run kubectl create -f $assets_folder/tprinst.yaml
}
