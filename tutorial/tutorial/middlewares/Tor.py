from scrapy import signals
import os
import requests
import time

from stem import Signal
from stem.control import Controller
from stem.util.log import get_logger

logger = get_logger()
logger.propagate = False

TOR_PROXY = 'http://localhost:8118'

class TorMiddleware(object):
    requests_count = 0
    requests_limit_for_change_ip = 3 

    def __init__(self):
        self.session = requests.Session()
        self.session.proxies = {'http': TOR_PROXY}

    def get_ip(self):
        return self.session.get('http://ipecho.net/plain').text

    def set_ip(self):
        current_ip = self.get_ip()
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
    
        while True:
            new_ip = self.get_ip()
            if new_ip == current_ip:
                time.sleep(1)
            else:
                break

    def process_request(self, request, spider):
        """
            You must first install the nc program and Tor service on your GNU Linux operating system
            After that and change /etc/tor/torrc, add
            control port and password to it.
            install privoxy for having HTTP and HTTPS over torSOCKS5
        """
        # Deploy : add controlport and password to /etc/tor/torrc
        # os.system("""(echo authenticate '"yourpassword"'; echo signal newnym; echo quit) | nc localhost 9051""")
        #request.meta['proxy'] = settings.get('HTTP_PROXY')

        self.requests_count += 1
        if self.requests_count > self.requests_limit_for_change_ip:
            self.set_ip()
            self.requests_count = 0 

        request.meta['proxy'] = TOR_PROXY

