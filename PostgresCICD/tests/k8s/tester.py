from kubernetes import client, config
import os
import base64

# temp set env vars
# these values will likely come from a config map
os.environ['NAMESPACE'] = 'postgres-dev'
os.environ['CLUSTER_NAME'] = 'hippo'

config.load_kube_config()
kube = client.CoreV1Api()

ns = os.getenv('NAMESPACE')
cluster_name = os.getenv('CLUSTER_NAME')


def run_tests():
    ip = get_cluster_ha_service_ip()
    primary = get_primary_postgres_pod()
    password = get_postgres_password()

    print(ip)
    print(primary)
    print(password)


def get_cluster_ha_service_ip():
    ha_svc = cluster_name + "-ha"
    services = kube.list_namespaced_service(namespace=ns)
    for svc in services.items:
        if svc.metadata.name == ha_svc:
            ip = svc.status.load_balancer.ingress[0].ip
            return ip


def get_primary_postgres_pod():
    primary_label = 'postgres-operator.crunchydata.com/role=master'
    pods = kube.list_namespaced_pod(namespace=ns, label_selector=primary_label)
    primary = pods.items[0].metadata.name
    return primary


def get_postgres_password():
    secret = cluster_name + "-pguser-postgres"
    secrets = kube.list_namespaced_secret(namespace=ns)

    for sec in secrets.items:
        if sec.metadata.name == secret:
            password = base64.b64decode(sec.data['password']).decode("utf-8")
            return password


# entry point
if __name__ == '__main__':
    run_tests()
