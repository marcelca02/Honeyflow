from kubernetes import client, config
import subprocess
from app.config import COWRIE_IMAGE

# def init_k8s():
#     config.load_kube_config()
#     v1 = client.CoreV1Api()
#     return v1

def create_cowrie_pod():
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/cowrie/pod_cowrie.yaml'])
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/cowrie/service_cowrie.yaml'])

def create_mailoney_pod():
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/mailoney/pod_mailoney.yaml'])
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/cowrie/service_mailoney.yaml'])

def create_heralding_pod():
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/heralding/pod_heralding.yaml'])
    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/heralding/service_heralding.yaml'])

def delete_pods():
    subprocess.run(['kubectl', 'delete', 'pod', 'cowrie'])
    subprocess.run(['kubectl', 'delete', 'pod', 'mailoney'])
    subprocess.run(['kubectl', 'delete', 'pod', 'heralding'])


# def get_pods(v1, namespace='default'):
#     return v1.list_namespaced_pod(namespace)

def delete_pod(name):
    subprocess.run(['kubectl', 'delete', 'pod', name])

