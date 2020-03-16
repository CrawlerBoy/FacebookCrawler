import random,base64
from mss.settings import PROXIES

class ProxyMiddleware(object):
  def process_request(self, request, spider):
    request.meta['proxy'] = "http://%s" % PROXIES


class PrintUrlMiddleware(object):
    def process_response(self, request, response, spider):
        print request.url + '-----------request'
        return response
