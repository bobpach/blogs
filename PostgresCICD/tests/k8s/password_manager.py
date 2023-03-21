""" Creates and provides access to a random;y generated password
"""
import string
import random
from kubernetes import client, config
import os
import base64


class PasswordManager:
    # temp set env vars
    # these values will likely come from a config map
    os.environ['NAMESPACE'] = 'postgres-dev'
    os.environ['CLUSTER_NAME'] = 'hippo'

    """ Creates and provides access to a random;y generated password
    """
    def __init__(self):
        if not hasattr(PasswordManager, 'postgres_password'):
            PasswordManager.postgres_password = self.get_postgres_password()
        if not hasattr(PasswordManager, 'test_db_password'):
            PasswordManager.test_db_password = self.generate_random_password()

    # @property
    # def test_db_password(self):
    #     """ Gets a randomly generated password

    #     Returns:
    #         string: Randomly generated password
    #     """
    #     return self._test_db_password

    # @property
    # def postgres_password(self):
    #     """ Gets a randomly generated password

    #     Returns:
    #         string: Randomly generated password
    #     """
    #     return self._postgres_password

    def generate_random_password(self):
        """ Generate random password of length 12 with letters,
        digits, and symbols
        """
        if not hasattr(self, '_test_db_password'):
            characters = string.ascii_letters + string.digits \
                + string.punctuation
            # self._test_db_password = ''.join(random.choice(characters)
            #                                  for i in range(12))
            pwd = ''.join(random.choice(characters)
                          for i in range(12))
            return pwd

    def get_postgres_password(self):
        config.load_kube_config()
        kube = client.CoreV1Api()
        ns = os.getenv('NAMESPACE')
        cluster_name = os.getenv('CLUSTER_NAME')

        secret = cluster_name + "-pguser-postgres"
        secrets = kube.list_namespaced_secret(namespace=ns)

        for sec in secrets.items:
            if sec.metadata.name == secret:
                pwd = base64.b64decode(sec.data['password']).decode("utf-8")
                return pwd
