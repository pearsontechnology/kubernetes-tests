#!/usr/bin/env bats

set -o pipefail

load helpers

# Infrastructure

@test "create tokens-test namespace" {
  kubectl create ns tokens-test
}

@test "add ns tokens" {
  /usr/local/bin/add_vault_tokens.sh tokens-test
}

@test "manually verify tokens" {
  export READ_TOKEN=`kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-read:" | awk '{print $NF}' | base64 -d`
  echo $READ_TOKEN | egrep -q "[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
  vault token-lookup $READ_TOKEN
  export WRITE_TOKEN=`kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-write:" | awk '{print $NF}' | base64 -d`
  echo $WRITE_TOKEN | egrep -q "[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
  vault token-lookup $WRITE_TOKEN
}

@test "check ns tokens" {
  READ_TOKEN=`kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-read:" | awk '{print $NF}' | base64 -d`
  READ_TOKEN_TTL=`vault token-lookup $READ_TOKEN | grep ^ttl | awk '{print $NF}'`
  WRITE_TOKEN=`kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-write:" | awk '{print $NF}' | base64 -d`
  WRITE_TOKEN_TTL=`vault token-lookup $WRITE_TOKEN | grep ^ttl | awk '{print $NF}'`
  sleep 2
  READ_TOKEN_TTL_NOW=`/usr/local/bin/renew_vault_tokens.sh check tokens-test | grep "^TTL\:" | awk '{print $2}' | head -1`
  result="$(expr $READ_TOKEN_TTL / $READ_TOKEN_TTL_NOW )"
  [ "$result" -eq 1 ]
  WRITE_TOKEN_TTL_NOW=`/usr/local/bin/renew_vault_tokens.sh check tokens-test | grep "^TTL\:" | awk '{print $2}' | tail -1`
  result="$(expr $WRITE_TOKEN_TTL / $WRITE_TOKEN_TTL_NOW )"
  [ "$result" -eq 1 ]
}

@test "renew ns tokens" {
  READ_TOKEN=`kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-read:" | awk '{print $NF}' | base64 -d`
  READ_TOKEN_TTL=`vault token-lookup $READ_TOKEN | grep ^ttl | awk '{print $NF}'`
  WRITE_TOKEN=`kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-write:" | awk '{print $NF}' | base64 -d`
  WRITE_TOKEN_TTL=`vault token-lookup $WRITE_TOKEN | grep ^ttl | awk '{print $NF}'`
  /usr/local/bin/renew_vault_tokens.sh renew tokens-test
  READ_TOKEN_TTL_NOW=`/usr/local/bin/renew_vault_tokens.sh check tokens-test | grep ^TTL\: | awk '{print $2}' | head -1`
  [ $READ_TOKEN_TTL_NOW -gt $READ_TOKEN_TTL ]
  WRITE_TOKEN_TTL_NOW=`/usr/local/bin/renew_vault_tokens.sh check tokens-test | grep ^TTL\: | awk '{print $2}' | tail -1`
  [ $WRITE_TOKEN_TTL_NOW -gt $WRITE_TOKEN_TTL ]
}

@test "regen ns tokens" {
  READ_TOKEN=`kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-read:" | awk '{print $NF}' | base64 -d`
  WRITE_TOKEN=`kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-write:" | awk '{print $NF}' | base64 -d`
  /usr/local/bin/renew_vault_tokens.sh regen tokens-test
  vault token-lookup $READ_TOKEN_NOW
  vault token-lookup $WRITE_TOKEN_NOW
  READ_TOKEN_NOW=`kubectl get --no-headers secret vault-tokens-test-read --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-read:" | awk '{print $NF}' | base64 -d`
  echo $READ_TOKEN_NOW | egrep -q "[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
  [ $READ_TOKEN_NOW != $READ_TOKEN ]
  WRITE_TOKEN_NOW=`kubectl get --no-headers secret vault-tokens-test-write --namespace=tokens-test -o yaml | grep -e ".\s*vault-tokens-test-write:" | awk '{print $NF}' | base64 -d`
  echo $WRITE_TOKEN_NOW | egrep -q "[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"
  [ $WRITE_TOKEN_NOW != $WRITE_TOKEN ]
}

@test "delete ns" {
  run kubectl delete ns tokens-test
  [ "$status" -eq 0 ]
  sleep 5
}

@test "ensure deleted secrets" {
  run /usr/local/bin/renew_vault_tokens.sh check tokens-test
  [ "$status" -eq 1 ]
}
