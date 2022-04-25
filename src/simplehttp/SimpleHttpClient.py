import requests
import time
from requests.exceptions import SSLError


class SimpleHttpClient:

    def __init__(self, logger = None):
        self.logger = logger

    # Function for performing a GET request using requests library with retries
    # Sets a 5 second timeout by default
    def get_request(self, url, parameters = None, timeout = 5):
        try:
            response = requests.get(url = url,
                                    params = parameters,
                                    timeout = timeout)
        except SSLError as s:
            if self.logger:
                self.logger.error('SSL Error:', s)

            for i in range(5, 0, -1):
                print('\rWaiting... ({})'.format(i), end = '')
                time.sleep(1)
            if self.logger:
                self.logger.warn('\rRetrying.' + ' ' * 10)

            # Recusively try again
            return self.get_request(url, parameters)

        if response:
            if self.logger:
                self.logger.debug('Got response {0}'.format(
                    response.status_code))
            return response
        else:
            # Response is none usually means too many requests. Wait and try again
            if self.logger:
                self.logger.warn('No response, waiting 10 seconds...')
            time.sleep(10)
            if self.logger:
                self.logger.warn('Retrying.')
            return self.get_request(url, parameters)
