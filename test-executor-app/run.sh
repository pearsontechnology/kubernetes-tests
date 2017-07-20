#!/bin/bash

stackips=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Stack,Values=${STACK_ID}" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
bastion=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Name,Values=bastion.${ENVIRONMENT}.kube" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
nfs=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Name,Values=nfs.${ENVIRONMENT}.kube" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
consulvaults=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Name,Values=consulvault-bitesize-${ENVIRONMENT}" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
vrouter=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Role,Values=vrouter" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
IPS=$stackips" "$bastion" "$nfs" "$vrouter" "$consulvaults

mkdir -p ~/.ssh
cp /etc/secret-volume/bitesize-priv-key ~/.ssh/bitesize.key
chmod 600 ~/.ssh/*

#Produce keyvalue pairs of hostnames to private ips. Would have liked to use kubectl
#here, but servicaaccounts only allow API access to namespace this test app is
#deployed in o. Will need to refactor this if we move away or expand outside AWS
echo "hosts:" >> /opt/testexecutor/hosts.yaml
for ip in $IPS;do
  hostname=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=private-ip-address,Values=${ip}" | jq '.Reservations[].Instances[] | .Tags[] | select(.Key=="Name") | .Value' | sed -e 's/\"//g'`
  echo "  - "name": "$hostname>> /opt/testexecutor/hosts.yaml
  echo "    "value": "$ip >> /opt/testexecutor/hosts.yaml
  ssh-keyscan $ip >> ~/.ssh/known_hosts > /dev/null 2>&1
done

kubectl config set-cluster ${ENVIRONMENT} --server=https://${KUBERNETES_SERVICE_HOST} --certificate-authority=/etc/secret-volume/kubectl-ca > /dev/null 2>&1
kubectl config set-credentials ${ENVIRONMENT}-admin --client-key=/etc/secret-volume/kubectl-client-key --username=admin --password=${KUBE_PASS} > /dev/null 2>&1
kubectl config set-context ${ENVIRONMENT} --cluster=${ENVIRONMENT} --user=${ENVIRONMENT}-admin > /dev/null 2>&1
kubectl config use-context ${ENVIRONMENT} > /dev/null 2>&1

python -u /opt/testexecutor/testRunner.py "/opt/testexecutor/hosts.yaml" $@
