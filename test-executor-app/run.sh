#!/bin/sh

export KUBE_TOKEN=`cat /var/run/secrets/kubernetes.io/serviceaccount/token`
export NAMESPACE=`cat /var/run/secrets/kubernetes.io/serviceaccount/namespace`

[ -f /var/hosts.yaml ] && rm -f /var/hosts.yaml

if [ -f /usr/local/bin/aws ]
then
  echo "Skipping AWS CLI Install"
else
  curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" > /dev/null 2>&1
  unzip awscli-bundle.zip > /dev/null 2>&1
  ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws > /dev/null 2>&1
fi

stackips=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Stack,Values=${STACK_ID}" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
bastion=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Name,Values=bastion.${ENVIRONMENT}.kube" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
nfs=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=tag:Name,Values=nfs.${ENVIRONMENT}.kube" "Name=instance-state-code,Values=16" | jq '.Reservations[].Instances[].PrivateIpAddress' | sed -e 's/\"//g'`
IPS=$stackips" "$bastion" "$nfs

mkdir -p ~/.ssh
cp /etc/secret-volume/bitesize-priv-key ~/.ssh/bitesize.key
chmod 600 ~/.ssh/*

#Produce keyvalue pairs of hostnames to private ips. Would have liked to use kubectl
#here, but servicaaccounts only allow API access to namespace this test app is
#deployed in o. Will need to refactor this if we move away or expand outside AWS
echo "hosts:" >> /var/hosts.yaml
for ip in $IPS;do
  hostname=`aws ec2 describe-instances --region=${REGION} --filters "Name=tag:Environment,Values=${ENVIRONMENT}" "Name=private-ip-address,Values=${ip}" | jq '.Reservations[].Instances[] | .Tags[] | select(.Key=="Name") | .Value' | sed -e 's/\"//g'`
  echo "  - "name": "$hostname>> /var/hosts.yaml
  echo "    "value": "$ip >> /var/hosts.yaml
  ssh-keyscan $ip >> ~/.ssh/known_hosts > /dev/null 2>&1
done

echo "KUBERNETES_VERSION: $KUBERNETES_VERSION"

curl -LO https://storage.googleapis.com/kubernetes-release/release/${KUBERNETES_VERSION}/bin/linux/amd64/kubectl
sudo cp kubectl /usr/local/bin
sudo chmod +x /usr/local/bin/kubectl

kubectl config set-cluster ${ENVIRONMENT} --server=https://${KUBERNETES_SERVICE_HOST} --certificate-authority=/etc/secret-volume/kubectl-ca
kubectl config set-credentials ${ENVIRONMENT}-admin --client-key=/etc/secret-volume/kubectl-client-key --username=admin --password=${KUBE_PASS}
kubectl config set-context ${ENVIRONMENT} --cluster=${ENVIRONMENT} --user=${ENVIRONMENT}-admin
kubectl config use-context ${ENVIRONMENT}

python -u /var/testRunner.py "/var/hosts.yaml" $@
