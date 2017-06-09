#!/usr/bin/env bats

set -o pipefail

load helpers

@test "test consul read and write" {
  curl -ks -X PUT -d 'test_value' https://consul.bitesize.${ENVIRONMENT}.${DOMAIN}/v1/kv/test/KEY1?token=${CONSUL_MASTER_TOKEN}
  curl -ks https://consul.bitesize.${ENVIRONMENT}.${DOMAIN}/v1/kv/test/KEY1?token=${CONSUL_MASTER_TOKEN} | jq '.[0].Value' | sed -e s/\"//g | base64 -d | grep test_value
}
