#!/usr/bin/env bats

set -o pipefail

@test "Verify that hello world app is responding through bitesize front end" {
    curlcmd="curl -m 5 -w \"%{http_code}\" -X POST -H \"Host: front.nodejs-hello-world-app.prsn-dev.io\" -H \"Content-Type: application/json\" -d \"{\"data\": \"blah\", \"username\": \"admin\", \"password\": \"password\"}\" http://front.nodejs-hello-world-app.prsn-dev.io | grep 200"
    masterip=`cat /opt/testexecutor/hosts.yaml | grep -A1 master | grep value | awk '{print $2}'`
    ssh -i ~/.ssh/bitesize.key -o StrictHostKeyChecking=no centos@$masterip $curlcmd
}
