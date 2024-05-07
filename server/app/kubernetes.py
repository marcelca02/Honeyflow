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

    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/cowrie/pod_cowrie.yaml'])
    subprocess.run(['kubectl', 'expose', 'pod', 'cowrie', '--type=NodePort', '--port=' + port, '--target-port=22', '--name=' + service_name, '--external-ip=0.0.0.0'])

def create_mailoney_pod():
    # # Comand line version
    service_name = 'mailoney-service'
    port = '8082'

    subprocess.run(['kubectl', 'apply', '-f', 'app/machines/mailoney/pod_mailoney.yaml'])
    # Esto ahora mismo no funciona
    subprocess.run(['kubectl', 'expose', 'pod', 'mailoney', '--type=NodePort', '--port=' + port, '--target-port=25','--name=' + service_name, '--external-ip=0.0.0.0'])


def get_pods(v1, namespace='default'):
    return v1.list_namespaced_pod(namespace)

def delete_pod(name):
    subprocess.run(['kubectl', 'delete', 'pod', name])

