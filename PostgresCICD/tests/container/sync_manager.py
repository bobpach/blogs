# from kubernetes import client, config
from logging_manager import LoggingManager
import urllib3
import requests
import os


class SyncManager:

    lm = LoggingManager()

    def synch_argocd_application(self):
        token = os.getenv("ARGOCD_TOKEN")
        
        LoggingManager.logger.debug(token)
        
        cookies = {'argocd.token': token.strip("\n")}
        # cookie = {'argocd.token':token}
        # cookie = {"argocd.token=%s" % (token)}
        print(cookies)
        LoggingManager.logger.debug(cookies)

        # config.load_incluster_config()
        # kube = client.CoreV1Api()

        # # TODO: add to cm
        # ns = "argocd"
        # svc_list = kube.list_namespaced_service(namespace=ns,
        #                                         field_selector="metadata."
        #                                         "name=argocd-server")
        # if svc_list is not None:
        #     ip = svc_list.items[0].status.loadBalancer.ingress.ip

        # TODO: throw error if list is empty

        ip = os.getenv("ARGOCD_SERVICE_ADDRESS")
        app_name = os.getenv("ARGOCD_APP_NAME").lower()
        # synch_url = 'https://34.148.254.19/api/v1/applications/test/sync'
        synch_url = 'https://%s/api/v1/applications/%s/sync' % (ip, app_name)
        LoggingManager.logger.debug("synch_url: %s" % (synch_url))
        verify_tls = os.getenv("ARGOCD_VERIFY_TLS").lower()

        if verify_tls == "true":
            verify = True
        else:
            verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            resp = requests.post(synch_url, cookies=cookies, verify=verify)
        except (Exception) as error:
            LoggingManager.logger.error(error, exc_info=True)

        LoggingManager.logger.info(resp)
        LoggingManager.logger.debug(resp.content)
