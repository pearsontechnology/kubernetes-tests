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
