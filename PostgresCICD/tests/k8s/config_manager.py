"""Contains ConfigManager Class

    Raises:
        Exception: database.ini parsing error for postgresql
        Exception: database.ini parsing error for testpostgresql

    Returns:
       dict: Dictionary containing postgres connection string values
"""
import os
from kubernetes import client, config
from password_manager import PasswordManager


class ConfigManager:
    """The ConfigManager Class

        Raises:
            Exception: database.ini parsing error for postgresql
            Exception: database.ini parsing error for testpostgresql

        Returns:
            dict: Dictionary containing postgres connection string values
    """

    pm = PasswordManager()

    def get_postgres_connection_parameters(self):
        params = self.get_common_connection_parameters()
        params["database"] = "postgres"
        params["user"] = "postgres"
        params["password"] = PasswordManager.postgres_password
        return params

    def get_test_db_connection_parameters(self):
        params = self.get_common_connection_parameters()
        params["database"] = "test_db"
        params["user"] = "test_user"
        params["password"] = PasswordManager.test_db_password
        return params

    def get_common_connection_parameters(self):
        params = {}
        params["host"] = self.get_cluster_ha_service_ip()
        params["port"] = 5432
        params["sslmode"] = "require"
        return params

    def get_cluster_ha_service_ip(self):
        config.load_kube_config()
        kube = client.CoreV1Api()
        ns = os.getenv('NAMESPACE')
        cluster_name = os.getenv('CLUSTER_NAME')
        ha_svc = cluster_name + "-ha"
        services = kube.list_namespaced_service(namespace=ns)
        for svc in services.items:
            if svc.metadata.name == ha_svc:
                ip = svc.status.load_balancer.ingress[0].ip
                return ip
