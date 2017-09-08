#!/usr/bin/python
import kubernetes

def test_cluster_autoscaler_adds_new_nodes():
    kubernetes.config.load_incluster_config()

    api = kubernetes.client.CoreV1Api()

    # Get list of initial minions
    try:
        nodes_list = api.list_node()
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->list_node: %s\n" % e)
    initial_minions = [ node.metadata.name for node in nodes_list.items if "master" not in node.metadata.name ]

    # Disable scheduling on all initial minions
    unschedulable = { "spec" : {"unschedulable" : True} }
    for minion in initial_minions:
        try:
            api_response = api.patch_node(minion, unschedulable)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->patch_node: %s\n" % e)

    # Create a pod. There will be nowhere to schedule it so cluster autoscaler should create a new minion.
    namespace = "test-runner"
    pod = {}
    pod['api_version'] = "v1"
    pod['Kind'] = "Pod"
    pod['metadata'] = {}
    pod['metadata']['name'] = "test-pod"
    pod['spec'] = {}
    pod['spec']['containers'] = []
    pod['spec']['containers'].append({})
    pod['spec']['containers'][0]['name'] = "bash"
    pod['spec']['containers'][0]['image'] = "bash:latest"

    try:
        pod = api.create_namespaced_pod(namespace, pod)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)

    # Wait for new node to be added.
    w = kubernetes.watch.Watch()
    for event in w.stream(api.list_node, timeout_seconds=900):
        if event['type'] == "ADDED":
            if event['object'].metadata.name not in [ node.metadata.name for node in nodes_list.items ]:
                w.stop()

    # Get current list of minions
    try:
        nodes_list = api.list_node()
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->list_node: %s\n" % e)
    current_minions = [ node.metadata.name for node in nodes_list.items if "master" not in node.metadata.name ]

    # Delete test-pod
    name = 'test-pod'
    namespace = 'test-runner'
    body = kubernetes.client.V1DeleteOptions()
    try:
        api_response = api.delete_namespaced_pod(name, namespace, body)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

    # Re-enable scheduling on all minions
    schedulable = { "spec" : {"unschedulable" : False} }
    for minion in initial_minions:
        try:
            api_response = api.patch_node(minion, schedulable)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->patch_node: %s\n" % e)

    assert len(current_minions) == len(initial_minions) + 1
