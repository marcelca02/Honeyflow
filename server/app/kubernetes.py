from kubernetes import client, config

def init_k8s():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1

def new_pod(name, image, v1, ports, namespace='default'):
    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name
        },
        "spec": {
            "containers": [{
                "name": name,
                "image": image,
                "ports": [{"containerPort": ports}]
            }]
        }
    }
    resp = v1.create_namespaced_pod(namespace, body=pod_manifest)
    return resp

def get_pods(v1, namespace='default'):
    return v1.list_namespaced_pod(namespace)

def delete_pod(name, v1, namespace='default'):
    return v1.delete_namespaced_pod(name, namespace)

