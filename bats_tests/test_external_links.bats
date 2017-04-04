#!/usr/bin/env bats

set -o pipefail

load helpers

# Infrastructure

@test "ssh master" {
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no master.${TF_VAR_environment}.${DOMAIN} 'test /etc/passwd'
}

