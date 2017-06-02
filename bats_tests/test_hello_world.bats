#!/usr/bin/env bats

set -o pipefail

@test "Verify that hello world app is responding through bitesize front end" {
    curl -s -m 5 -o /dev/null -w "%{http_code}" -X POST -H 'Host: front.nodejs-hello-world-app.prsn-dev.io' -H "Content-Type: application/json" -d '{"data": "blah", "username": "admin", "password": "password"}' http://front.nodejs-hello-world-app.prsn-dev.io | grep 200
}
