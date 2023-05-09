# from kubernetes import client, config
from logging_manager import LoggingManager
import urllib3
import requests
import os


class SyncManager:

    lm = LoggingManager()

    def synch_argocd_application(self):
        token = os.getenv("ARGOCD_TOKEN")

        cookies = {'argocd.token': token.strip("\n")}
        LoggingManager.logger.debug(cookies)

        ip = os.getenv("ARGOCD_SERVICE_ADDRESS")
        app_name = os.getenv("ARGOCD_APP_NAME").lower()

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
