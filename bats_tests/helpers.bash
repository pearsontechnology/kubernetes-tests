#!/bin/bash

# Should match minion_count in terraform.tfvars
MINION_COUNT=${MINION_COUNT}

LOADBALANCER_COUNT=3

# values_equal takes 2 values, both must be non-null and equal
values_equal () {
  if [[ "X$1" != "X" ]] || [[ "X$2" != "X" ]] && [[ $1 == $2 ]]; then
    return 0
  else
    return 1
  fi
}

run_command_on_master() {
  masterip=`cat /opt/testexecutor/hosts.yaml | grep -A1 master | grep value | awk '{print $2}'`
  ssh -i ~/.ssh/bitesize.key  -o StrictHostKeyChecking=no centos@${masterip} $1
}
wait-for-code() {
  count=0
  while [ "$count" -le 24 ]; do
    $1
    if [ "$status" -eq $2 ]; then
      break
    else
      count=$((count+1))
      sleep 5
    fi
  done
}
# min_value_met takes 2 values, both must be non-null and 2 must be equal or greater than 1
min_value_met () {
  if [[ "X$1" != "X" ]] || [[ "X$2" != "X" ]] && [[ $2 -ge $1 ]]; then
    return 0
  else
    return 1
  fi
}

filtered_ingress_logs_eq_0 () {
  ingresses=$1
  filter=$2
  for pod in $ingresses; do
    lineCount=`kubectl exec -it --namespace=kube-system $pod -- cat /etc/nginx/nginx.conf | grep "$filter" | wc -l`
    if [ $lineCount -gt 0 ]; then
      return 1
    fi
  done
  return 0
}

filtered_ingress_logs_gt_0 () {
  ingresses=$1
  filter=$2
  for pod in $ingresses; do
    lineCount=`kubectl exec -it --namespace=kube-system $pod -- cat /etc/nginx/nginx.conf | grep "$filter" | wc -l`
    if [ $lineCount -eq 0 ]; then
      return 1
    fi
  done
  return 0
}
