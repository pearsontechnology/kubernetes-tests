#!/usr/bin/env bats

set -o pipefail
load helpers
@test "Verify that hello world app is responding through bitesize front end" {
    curlcmd="curl -m 5 -w \"%{http_code}\" -X POST -H \"Host: front.nodejs-hello-world-app.prsn-dev.io\" -H \"Content-Type: application/json\" -d \"{\"data\": \"blah\", \"username\": \"admin\", \"password\": \"password\"}\" http://front.nodejs-hello-world-app.prsn-dev.io | grep 200"
    run_command_on_master $curlcmd
}
