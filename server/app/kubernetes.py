from kubernetes import client, config
import subprocess
from app.config import COWRIE_IMAGE

def init_k8s():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1


def create_cowrie_pod(v1, namespace='default'):
    # # Comand line version
    service_name = 'cowrie-service'
    port = '8081'

    subprocess.run(['kubectl', 'apply', '-f', 'machines/cowrie/cowrie.yaml'])
    subprocess.run(['kubectl', 'expose', 'pod', 'cowrie', 'type=NodePort', '--port=' + port, '--targetPort=22', '--name=' + service_name])

def create_mailoney_pod():
    # # Comand line version
    service_name = 'mailoney-service'
    port = '8082'

    subprocess.run(['kubectl', 'apply', '-f', 'machines/mailoney/mailoney.yaml'])
    subprocess.run(['kubectl', 'expose', 'pod', 'mailoney', 'type=NodePort', '--port=' + port, '--targetPort=25', '--name=' + service_name])


def get_pods(v1, namespace='default'):
    return v1.list_namespaced_pod(namespace)

def delete_pod(name, v1, namespace='default'):
    return v1.delete_namespaced_pod(name, namespace)

