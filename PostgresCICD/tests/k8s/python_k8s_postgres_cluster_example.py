import os
from kubernetes import client, config

os.environ['NAMESPACE'] = 'postgres-dev'

config.load_kube_config()
kube = client.CoreV1Api()
ns = os.getenv('NAMESPACE')


def get_pods():
    postgres_pods = kube.list_namespaced_pod(namespace=ns)
    for pod in postgres_pods.items:
        print(pod.metadata.name)


def get_postgres_cluster_pods():
    cluster_label = 'postgres-operator.crunchydata.com/cluster=hippo'
    cluster_pods = kube.list_namespaced_pod(namespace=ns,
                                            label_selector=cluster_label)
    for pod in cluster_pods.items:
        print(pod.metadata.name)


def get_postgres_database_pods():
    postgres_label = 'postgres-operator.crunchydata.com/data=postgres'
    postgres_pods = kube.list_namespaced_pod(namespace=ns,
                                             label_selector=postgres_label)
    for pod in postgres_pods.items:
        print(pod.metadata.name)


def get_primary_postgres_pod():
    primary_label = 'postgres-operator.crunchydata.com/role=master'
    pods = kube.list_namespaced_pod(namespace=ns, label_selector=primary_label)
    for pod in pods.items:
        print(pod.metadata.name)


# entry point
if __name__ == '__main__':
    print("*** Printing All Pods in Namespace ***")
    get_pods()
    print("*** Printing All Postgres Cluster Pods in Namespace ***")
    get_postgres_cluster_pods()
    print("*** Printing All Postgres Database Pods in Namespace ***")
    get_postgres_database_pods()
    print("*** Printing All Postgres Primary Pods in Namespace ***")
    get_primary_postgres_pod()
