#!/usr/bin/env bats

set -o pipefail

load helpers

# Infrastructure

@test "ssh master" {
  # This need to run after running - python tools/migrate_cluster.py --env <tikky6> --region <us-east-1>
  ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no master.${ENVIRONMENT}.${DOMAIN} 'test /etc/passwd'
}

