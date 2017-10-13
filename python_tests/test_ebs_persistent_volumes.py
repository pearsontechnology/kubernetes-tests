#!/usr/bin/python
import kubernetes
import time
import boto3
import os

def test_ebs_persistent_volumes():
    # Define environment
    kubernetes.config.load_incluster_config()
    api = kubernetes.client.CoreV1Api()
    namespace = "test-runner"
    client = boto3.client('ec2', region_name=os.environ["REGION"])

    # Get list of nodes
    try:
        nodes_list = api.list_node()
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->list_node: %s\n" % e)

    # Remove master node from the list
    nodes_list.items = [node for node in nodes_list.items if node.metadata.labels['role'] != "master"]

    # Look for two nodes in the same AZ
    try:
        nodes_in_same_az = list()
        while len(nodes_in_same_az) < 2 and len(nodes_list.items) > 0:
            nodes_in_same_az = list()
            nodes_in_same_az.append(nodes_list.items[0])
            del nodes_list.items[0]
            for node in nodes_list.items:
                if node.metadata.labels['failure-domain.beta.kubernetes.io/zone'] == nodes_in_same_az[0].metadata.labels['failure-domain.beta.kubernetes.io/zone']:
                    nodes_in_same_az.append(node)

        if len(nodes_in_same_az) < 2:
            raise Error("Cluster does not have at least 2 nodes in the same availability zone")
    except ValueError as err:
        print("Exception while running test: %s\n" % err)

    # Define a PVC object
    pvc = {}
    pvc['api_version'] = "v1"
    pvc['Kind'] = "PersistentVolumeClaim"
    pvc['metadata'] = {}
    pvc['spec'] = {}
    pvc['spec']['accessModes'] = [ "ReadWriteOnce" ]
    pvc['spec']['resources'] = {}
    pvc['spec']['resources']['requests'] = {}
    pvc['spec']['resources']['requests']['storage'] = "5Gi"

    # Ensure the PVC's corresponding EBS vol gets created in the same AZ as the two nodes.
    # Our version of kubernetes.io/aws-ebs just does round robin across AZs
    # You cannot specify which AZ to use :(
    index = 0
    test_pvcs = list()
    while True:
        pvc['metadata']['name'] = "test-pvc" + str(index)

        try:
            created_pvc = api.create_namespaced_persistent_volume_claim(namespace, pvc)
            time.sleep(10)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_persistent_volume_claim: %s\n" % e)

        test_pvcs.append(pvc['metadata']['name'])

        ebs_vol = client.describe_volumes(
            Filters=[
                {
                    'Name': 'tag:kubernetes.io/created-for/pvc/namespace',
                    'Values': [ namespace, ],
                },
                {
                    'Name': 'tag:kubernetes.io/created-for/pvc/name',
                    'Values': [ pvc['metadata']['name'], ],
                },
                    ],
                   )

        if ebs_vol['Volumes'][0]['AvailabilityZone'] == nodes_in_same_az[0].metadata.labels['failure-domain.beta.kubernetes.io/zone']:
            break
        else:
            index += 1

    # Create a test pod with a PV attached to the first node.
    pod = {}
    pod['api_version'] = "v1"
    pod['Kind'] = "Pod"
    pod['metadata'] = {}
    pod['metadata']['name'] = "test-pod"
    pod['spec'] = {}
    pod['spec']['nodeSelector'] = {}
    pod['spec']['nodeSelector']['kubernetes.io/hostname'] = nodes_in_same_az[0].metadata.name
    pod['spec']['volumes'] = list()
    pod['spec']['volumes'].append({})
    pod['spec']['volumes'][0]['name'] = "ebs-pv"
    pod['spec']['volumes'][0]['persistentVolumeClaim'] = {}
    pod['spec']['volumes'][0]['persistentVolumeClaim']['claimName'] = pvc['metadata']['name']
    pod['spec']['containers'] = []
    pod['spec']['containers'].append({})
    pod['spec']['containers'][0]['name'] = "writer"
    pod['spec']['containers'][0]['image'] = "pearsontechnology/test-ebs-pvc:6"
    pod['spec']['containers'][0]['volumeMounts'] = []
    pod['spec']['containers'][0]['volumeMounts'].append({})
    pod['spec']['containers'][0]['volumeMounts'][0]['mountPath'] = "/tmp/pv"
    pod['spec']['containers'][0]['volumeMounts'][0]['name'] = "ebs-pv"
    try:
        api_response = api.create_namespaced_pod(namespace, pod)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)

    # Wait for pod to start and write the testdata
    name = "test-pod"
    index = 0
    while True:
        time.sleep(1)
        try:
            created_pod = api.read_namespaced_pod_status(name, namespace)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e)
        if created_pod.status.phase == "Running":
            break
        else:
            index += 1
        if index > 120:
            print("120 second timeout exceeded waiting for test-pod to start")
            break

    # Delete test-pod
    name = "test-pod"
    body = {}
    body['grace_period_seconds'] = 0
    try:
        api_response = api.delete_namespaced_pod(name, namespace, body)
        time.sleep(90)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

    # Move test-pod to second node
    pod['spec']['nodeSelector']['kubernetes.io/hostname'] = nodes_in_same_az[1].metadata.name
    pod['spec']['containers'][0]['name'] = "bash"
    pod['spec']['containers'][0]['image'] = "bash:latest"
    pod['spec']['containers'][0]['command'] = []
    pod['spec']['containers'][0]['command'].append("/bin/sleep")
    pod['spec']['containers'][0]['args'] = []
    pod['spec']['containers'][0]['args'].append("600")
    try:
        pod = api.create_namespaced_pod(namespace, pod)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)

    # Wait for pod to start
    name = "test-pod"
    index = 0
    while True:
        time.sleep(1)
        try:
            created_pod = api.read_namespaced_pod_status(name, namespace)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_pod_status: %s\n" % e)
        if created_pod.status.phase == "Running":
            break
        else:
            index += 1
        if index > 120:
            print("120 second timeout exceeded waiting for test-pod to start")
            break

    # Exec into the pod and check we can retreive previously written data
    cmd = [ "cat", "/tmp/pv/testdata" ]
    try:
        exec_response = api.connect_post_namespaced_pod_exec(name="test-pod", namespace="test-runner", command=cmd, stderr=True, stdin=True, stdout=True, tty=False)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->connect_post_namespaced_pod_exec: %s\n" % e)

    # Delete test-pod
    name = 'test-pod'
    namespace = 'test-runner'
    body = kubernetes.client.V1DeleteOptions()
    try:
        api_response = api.delete_namespaced_pod(name, namespace, body)
    except kubernetes.client.rest.ApiException as e:
        print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

    # Delete PVCs
    body = kubernetes.client.V1DeleteOptions()
    for pvc_name in test_pvcs:
        try:
            api_response = api.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace, body=body)
        except kubernetes.client.rest.ApiException as e:
            print("Exception when calling CoreV1Api->delete_namespaced_persistent_volume_claim: %s\n" % e)

    assert exec_response.strip() == "testdata"
