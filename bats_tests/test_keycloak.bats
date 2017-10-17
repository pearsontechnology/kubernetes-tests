#!/usr/bin/env bats

set -o pipefail

load helpers

# Keycloak RDS

@test "keycloak rds instance" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi

  aws rds describe-db-instances --region=${REGION} --query "DBInstances[?DBName==\`${ENVIRONMENT}keycloakrds\`].DBInstanceStatus" --output=text | grep "^available$"
}

@test "keycloak web ui" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi

  curl -sk -o /dev/null -w "%{http_code}" https://auth-prelive.${ENVIRONMENT}.${DOMAIN}/auth/ | grep 200
}

@test "keycloak verify token access for kubernetes client" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi

  # k8sadmin-${ENVIRONMENT} must be in the operations group for full privileges
  curl -k -X POST -d "username=k8sadmin-${ENVIRONMENT}" \
  -d "password=${KUBE_PASS}" \
  -d grant_type=password \
  -d "client_id=kubernetes-${ENVIRONMENT}" \
  https://auth-prelive.${ENVIRONMENT}.${DOMAIN}/auth/realms/master/protocol/openid-connect/token \
  | jq .access_token | cut -d. -f2 | base64 -d | jq -r ".groups" | grep "operations"

}
