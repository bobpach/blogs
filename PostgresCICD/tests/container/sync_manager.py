from kubernetes import client, config
from logging_manager import LoggingManager
import requests
import os


class SyncManager:

    lm = LoggingManager()

    def synch_argocd_application(self):
        token = os.getenv("ARGOCD_TOKEN")
        cookies = {'argocd.token': token}

        config.load_incluster_config()
        kube = client.CoreV1Api()

        # TODO: add to cm
        ns = "argocd"
        svc_list = kube.list_namespaced_service(namespace=ns,
                                                name="argocd-server")

        if svc_list is not None:
            ip = svc_list.items[0].status.loadBalancer.ingress.ip

        # TODO: throw error if list is empty

        app_name = os.getenv("ARGOCD_APP_NAME").lower()
        # synch_url = 'https://34.148.254.19/api/v1/applications/test/sync'
        synch_url = "https://%s/api/v1/applications/%s/sync" % (ip, app_name)
        verify_tls = os.getenv("ARGOCD_VERIFY_TLS").lower()
        if verify_tls == "true":
            verify = True
        else:
            verify = False
        try:
            resp = requests.post(synch_url, cookies=cookies, verify=verify)
        except (Exception) as error:
            LoggingManager.logger.error(error, exc_info=True)

        LoggingManager.logger.info(resp)
        LoggingManager.logger.debug(resp.content)
