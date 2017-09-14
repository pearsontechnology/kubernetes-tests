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

  curl -sk -o /dev/null -w "%{http_code}" https://auth.${ENVIRONMENT}${DOMAIN}/auth/ | grep 200
}

@test "keycloak get token for kubernetes client" {
  if [ $BRAIN != "true" ]; then
    skip "Not brain"
  fi

  curl -sk -I -X POST -d "username=k8sadmin-${ENVIRONMENT}" -d "password=${KEYCLOAK_PASSWORD}" -d grant_type=password -d "client_id=kubernetes-${ENVIRONMENT}" https://auth.${ENVIRONMENT}${DOMAIN}/auth/realms/master/protocol/openid-connect/token

}
