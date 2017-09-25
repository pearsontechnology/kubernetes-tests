import json
import requests

# Check a random container to see if heapster is collecting the CPU metric.
def test_heapster_is_collecting_container_cpu_metric():
    req = requests.get("http://heapster.kube-system.svc.cluster.local/apis/metrics/v1alpha1/namespaces/kube-system/pods")
    cpu_metric = ""
    for pod in json.loads(req.text)['items']:
        for c in pod['containers']:
            if c['name'] == "kube-apiserver":
                cpu_metric = c['usage']['cpu']
    assert(cpu_metric != "")
