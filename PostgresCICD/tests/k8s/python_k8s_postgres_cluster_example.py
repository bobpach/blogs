"""Sample functions to show how to interact with PGO pods in kubernetes
"""
import os
from kubernetes import client, config

# setting an environment variable
# in a container this could be done via a configmap
os.environ['NAMESPACE'] = 'postgres-dev'

# connecting to kubernetes using local context
# there are various config load options
# in a container use config.load_incluster_config()
config.load_kube_config()
kube = client.CoreV1Api()

# getting namespace from environment variable
ns = os.getenv('NAMESPACE')


def get_pods():
    """ List all pod names in a namespace
    """
    postgres_pods = kube.list_namespaced_pod(namespace=ns)
    for pod in postgres_pods.items:
        print(pod.metadata.name)


def get_postgres_cluster_pods():
    """ List all postgres cluster pods
    """
    cluster_label = 'postgres-operator.crunchydata.com/cluster=hippo'
    cluster_pods = kube.list_namespaced_pod(namespace=ns,
                                            label_selector=cluster_label)
    for pod in cluster_pods.items:
        print(pod.metadata.name)


def get_postgres_database_pods():
    """ List all postgres database pods
    """
    postgres_label = 'postgres-operator.crunchydata.com/data=postgres'
    postgres_pods = kube.list_namespaced_pod(namespace=ns,
                                             label_selector=postgres_label)
    for pod in postgres_pods.items:
        print(pod.metadata.name)


def get_primary_postgres_pod():
    """ List all postgres primary pods
    """
    primary_label = 'postgres-operator.crunchydata.com/role=master'
    primary_pods = kube.list_namespaced_pod(namespace=ns,
                                            label_selector=primary_label)
    for pod in primary_pods.items:
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
