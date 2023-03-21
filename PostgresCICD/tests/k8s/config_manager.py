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

    # initialize PasswordManager
    pm = PasswordManager()

    def get_postgres_connection_parameters(self):
        """ Add postgres db connection parameters to the collection

        Returns:
            dictionary: Contains postgres db connection parameters
        """
        params = self.get_common_connection_parameters()
        params["database"] = "postgres"
        params["user"] = "postgres"
        params["password"] = PasswordManager.postgres_password
        return params

    def get_test_db_connection_parameters(self):
        """ Add test db connection parameters to the collection

        Returns:
            dictionary: Contains test db connection parameters
        """
        params = self.get_common_connection_parameters()
        params["database"] = "test_db"
        params["user"] = "test_user"
        params["password"] = PasswordManager.test_db_password
        return params

    # TODO: port and sslmode an come from cluster configmaps
    def get_common_connection_parameters(self):
        """ Create common connection parameter collection

        Returns:
            dictionary: Contains common db connection parameters
        """
        params = {}
        params["host"] = self.get_cluster_ha_service_ip()
        params["port"] = 5432
        params["sslmode"] = "require"
        return params

    # TODO: switch to internal IP when loading into a container
    def get_cluster_ha_service_ip(self):
        """ Gets the ip address for the cluster ha service

        Returns:
            string: cluster ha service ip address
        """
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
