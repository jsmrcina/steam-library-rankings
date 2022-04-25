import requests
import time
import logging
from requests.exceptions import SSLError


class SimpleHttpClient:

    # Function for performing a GET request using requests library with retries
    # Sets a 5 second timeout by default
    def get_request(self, url, parameters = None, timeout = 5):
        try:
            response = requests.get(url = url,
                                    params = parameters,
                                    timeout = timeout)
        except SSLError as s:
            logging.error('SSL Error:', s)

            for i in range(5, 0, -1):
                print('\rWaiting... ({})'.format(i), end = '')
                time.sleep(1)
            logging.warn('\rRetrying.' + ' ' * 10)

            # Recusively try again
            return self.get_request(url, parameters)

        if response:
            logging.debug(f'Got response {response.status_code}')
            return response
        else:
            # Response is none usually means too many requests. Wait and try again
            logging.warn('No response, waiting 10 seconds...')
            time.sleep(10)
            logging.warn('Retrying.')
            return self.get_request(url, parameters)
