import requests
import os

VCLOUD_AUTH_HEADER = 'x-vcloud-authorization'
VCLOUD_VERSION = '1.5'
VCLOUD_MIME = 'application/*+xml;version=%s' % VCLOUD_VERSION
AUTH_ENV = 'VCLOUD_AUTH_TOKEN'

class VCloud(object):

    def __init__(self, api=None):
        self.key = api or os.environ[AUTH_ENV]

    def req(self, url):
        headers = {"Accept": VCLOUD_MIME,
                   VCLOUD_AUTH_HEADER: self.key}

        return requests.get(url, headers=headers, verify=False)
