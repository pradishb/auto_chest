''' Moudule for league client communication '''
import time
import threading

import requests
import urllib3
import lcu_connector_python as lcu


from settings import LEAGUE_CLIENT_LOCATION, CONNECTION_READ_INTERVAL


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ClientConnectionException(Exception):
    ''' Raised when there is error when connecting to league client '''


class Connection:
    ''' Connects to league client and communicates with it '''

    def __init__(self):
        self.kwargs = None
        self.url = None
        get_connection_thread = threading.Thread(
            target=self.get_connection_loop, daemon=True)
        get_connection_thread.start()

    def get_connection_loop(self):
        ''' Parses connection in a certain interval '''
        while True:
            self.get_connection()
            time.sleep(CONNECTION_READ_INTERVAL)

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        connection = lcu.connect(LEAGUE_CLIENT_LOCATION)
        if connection == 'Ensure the client is running and that you supplied the correct path':
            self.kwargs = None
            self.url = None
            return
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']

    def get(self, url, *args, **kwargs):
        ''' Wrapper around requests get method '''
        return requests.get('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def post(self, url, *args, **kwargs):
        ''' Wrapper around requests post method '''
        return requests.post('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def patch(self, url, *args, **kwargs):
        ''' Wrapper around requests patch method '''
        return requests.patch('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)

    def put(self, url, *args, **kwargs):
        ''' Wrapper around requests put method '''
        return requests.put('{}{}'.format(self.url, url), *args, **kwargs, **self.kwargs)
