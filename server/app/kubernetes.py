from kubernetes import client, config
import subprocess
from app.config import COWRIE_IMAGE

def init_k8s():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    return v1


def create_cowrie_pod(v1, namespace='default'):
    # # Comand line version
    service_name = 'cowrie'
    port = '8081'


    subprocess.run(['kubectl', 'run', 'cowrie', '--image', COWRIE_IMAGE, '--port', '22'])  
    subprocess.run(['kubectl', 'expose', 'pod', 'cowrie', 'type=NodePort', '--port=' + port, '--targetPort=22', '--name=' + service_name])


    # # kubernetes client library version
    # pod = {
    #     'apiVersion': 'v1',
    #     'kind': 'Pod',
    #     'metadata': {
    #         'name': 'cowrie',
    #     },
    #     'spec': {
    #         'containers': [
    #             {
    #                 'name': 'cowrie',
    #                 'image': COWRIE_IMAGE,
    #             }
    #         ]
    #     }
    # }
    # v1.create_namespaced_pod(namespace, pod)
    #
    # service = {
    #     'apiVersion': 'v1',
    #     'kind': 'Service',
    #     'metadata': {
    #         'name': 'cowrie',
    #     },
    #     'spec': {
    #         'ports': [
    #             {
    #                 'protocol': 'TCP',
    #                 'port': 22,
    #                 'targetPort': 40550,
    #             },
    #             {
    #                 'protocol': 'TCP',
    #                 'port': 23,
    #                 'targetPort': 40551,
    #             }
    #         ]
    #     }
    # }
    #
    # v1.create_namespaced_service(namespace, service)



def get_pods(v1, namespace='default'):
    return v1.list_namespaced_pod(namespace)

def delete_pod(name, v1, namespace='default'):
    return v1.delete_namespaced_pod(name, namespace)

