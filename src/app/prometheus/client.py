from urllib.parse import urlparse
import os
import json
import logging
import numpy
from datetime import datetime, timedelta
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


_LOGGER = logging.getLogger(__name__)

from app.config.settings import _config

# In case of a connection failure try 2 more times
MAX_REQUEST_RETRIES = 3
# wait 1 second before retrying in case of an error
RETRY_BACKOFF_FACTOR = 1
# retry only on these status
RETRY_ON_STATUS = [408, 429, 500, 502, 503, 504]

class PromClient(object):

    def __init__(self, *args, **kwargs):
        self.api_url = _config.prometheus + '/api/v0/'

        if retry is None:
            retry = Retry(
                total=MAX_REQUEST_RETRIES,
                backoff_factor=RETRY_BACKOFF_FACTOR,
                status_forcelist=RETRY_ON_STATUS,
            )
        self.session = requests.Session()
        self._session.mount(self.url, HTTPAdapter(max_retries=retry))

    def check_prometheus_connection(self, params: dict = None) -> bool:
        response = self._session.get(
            "{0}/".format(_config.prometheus),
            verify= _config.ssl_verification,
            params=params,
        )
        return response.ok