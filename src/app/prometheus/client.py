from app.config.settings import _config
from urllib.parse import urlparse
import os
import json
import logging
import numpy
import asyncio
from datetime import datetime, timedelta
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app.prometheus.exceptions import PrometheusApiClientException


_LOGGER = logging.getLogger(__name__)


# In case of a connection failure try 2 more times
MAX_REQUEST_RETRIES = 3
# wait 1 second before retrying in case of an error
RETRY_BACKOFF_FACTOR = 1
# retry only on these status
RETRY_ON_STATUS = [408, 429, 500, 502, 503, 504]


class PromClient(object):

    def __init__(self, *args, **kwargs):
        """
        Initializes a session with the Prometheus API by setting the API URL and
        creating a new requests session with retry settings. 

        Args:
            *args: variable length argument list
            **kwargs: arbitrary keyword arguments

        Returns:
            None
        """
        self.api_url = _config.prometheus + '/api/v1'
        retry = Retry(
            total=MAX_REQUEST_RETRIES,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_ON_STATUS,
        )
        self._session = requests.Session()
        self._session.mount(_config.prometheus, HTTPAdapter(max_retries=retry))

    def check_prometheus_connection(self, params: dict = None) -> bool:
        """
        Checks the connection to Prometheus. 

        :param params: A dictionary of query string parameters to include in the request.
        :type params: dict, optional
        :return: A boolean indicating whether the response was successful.
        :rtype: bool
        """
        response = self._session.get(
            "{0}/".format(_config.prometheus),
            verify=_config.ssl_verification,
            params=params,
        )
        return response.ok

    def get_alerts(self):
        """
        Get alerts from the Prometheus API.

        :return: A list containing alert data.
        :raises PrometheusApiClientException: If the API returns a non-200 response.
        """
        data = []

        response = self._session.get(
            '{}/alerts'.format(self.api_url),
            verify=_config.ssl_verification,
        )
        if response.status_code == 200:
            data += response.json()["data"]["alerts"]
        else:
            raise PrometheusApiClientException(
                "HTTP Status Code {} ({!r})".format(
                    response.status_code, response.content)
            )
        return data

    def get_metric_range_data(
        self,
        metric_name: str,
        label_config: dict = None,
        start_time: datetime = (datetime.now() - timedelta(minutes=10)),
        end_time: datetime = datetime.now(),
        chunk_size: timedelta = None,
        store_locally: bool = False,
        params: dict = None,
    ):
        r"""
        Get the current metric value for the specified metric and label configuration.
        :param metric_name: (str) The name of the metric.
        :param label_config: (dict) A dictionary specifying metric labels and their
            values.
        :param start_time:  (datetime) A datetime object that specifies the metric range start time.
        :param end_time: (datetime) A datetime object that specifies the metric range end time.
        :param chunk_size: (timedelta) Duration of metric data downloaded in one request. For
            example, setting it to timedelta(hours=3) will download 3 hours worth of data in each
            request made to the prometheus host
        :param store_locally: (bool) If set to True, will store data locally at,
            `"./metrics/hostname/metric_date/name_time.json.bz2"`
        :param params: (dict) Optional dictionary containing GET parameters to be
            sent along with the API request, such as "time"
        :return: (list) A list of metric data for the specified metric in the given time
            range
        :raises:
            (RequestException) Raises an exception in case of a connection error
            (PrometheusApiClientException) Raises in case of non 200 response status code
        """
        params = params or {}
        data = []

        _LOGGER.debug("start_time: %s", start_time)
        _LOGGER.debug("end_time: %s", end_time)
        _LOGGER.debug("chunk_size: %s", chunk_size)

        if not (isinstance(start_time, datetime) and isinstance(end_time, datetime)):
            raise TypeError(
                "start_time and end_time can only be of type datetime.datetime")

        if not chunk_size:
            chunk_size = end_time - start_time
        if not isinstance(chunk_size, timedelta):
            raise TypeError(
                "chunk_size can only be of type datetime.timedelta")

        start = round(start_time.timestamp())
        end = round(end_time.timestamp())

        if (end_time - start_time).total_seconds() < chunk_size.total_seconds():
            raise ValueError("specified chunk_size is too big")
        chunk_seconds = round(chunk_size.total_seconds())

        if label_config:
            label_list = [str(key + "=" + "'" + label_config[key] + "'")
                          for key in label_config]
            query = metric_name + "{" + ",".join(label_list) + "}"
        else:
            query = metric_name
        _LOGGER.debug("Prometheus Query: %s", query)

        while start < end:
            if start + chunk_seconds > end:
                chunk_seconds = end - start

            # using the query API to get raw data
            response = self._session.get(
                "{0}/query".format(self.api_url),
                params={
                    **{
                        "query": query + "[" + str(chunk_seconds) + "s" + "]",
                        "time": start + chunk_seconds,
                    },
                    **params,
                },
                verify=_config.ssl_verification
            )
            if response.status_code == 200:
                data += response.json()["data"]["result"]
            else:
                raise PrometheusApiClientException(
                    "HTTP Status Code {} ({!r})".format(
                        response.status_code, response.content)
                )
            if store_locally:
                # store it locally
                self._store_metric_values_local(
                    metric_name,
                    json.dumps(response.json()["data"]["result"]),
                    start + chunk_seconds,
                )

            start += chunk_seconds
        return data

    async def get_metric_range_data_async(
        self,
        metric_name: str,
        label_config: dict = None,
        start_time: datetime = (datetime.now() - timedelta(minutes=10)),
        end_time: datetime = datetime.now(),
        chunk_size: timedelta = None,
        store_locally: bool = False,
        params: dict = None,
    ):
        """
        Asynchronously retrieves a range of data points for a given Prometheus metric.

        :param metric_name: The name of the Prometheus metric to retrieve data for.
        :type metric_name: str

        :param label_config: A dictionary of labels to filter the Prometheus query with. Defaults to None.
        :type label_config: dict, optional

        :param start_time: The starting time from which to retrieve data. Defaults to 10 minutes ago.
        :type start_time: datetime, optional

        :param end_time: The ending time to retrieve data up until. Defaults to the current time.
        :type end_time: datetime, optional

        :param chunk_size: The size of the time chunks to retrieve data in. Defaults to None.
        :type chunk_size: timedelta, optional

        :param store_locally: Whether or not to store the retrieved data locally. Defaults to False.
        :type store_locally: bool, optional

        :param params: Any additional parameters to include in the query. Defaults to None.
        :type params: dict, optional

        :return: A list of data points for the given metric.
        :rtype: list
        """
        params = params or {}
        data = []

        _LOGGER.debug("start_time: %s", start_time)
        _LOGGER.debug("end_time: %s", end_time)
        _LOGGER.debug("chunk_size: %s", chunk_size)

        if not (isinstance(start_time, datetime) and isinstance(end_time, datetime)):
            raise TypeError(
                "start_time and end_time can only be of type datetime.datetime")

        if not chunk_size:
            chunk_size = end_time - start_time
        if not isinstance(chunk_size, timedelta):
            raise TypeError(
                "chunk_size can only be of type datetime.timedelta")

        start = round(start_time.timestamp())
        end = round(end_time.timestamp())

        if (end_time - start_time).total_seconds() < chunk_size.total_seconds():
            raise ValueError("specified chunk_size is too big")
        chunk_seconds = round(chunk_size.total_seconds())

        if label_config:
            label_list = [str(key + "=" + "'" + label_config[key] + "'")
                          for key in label_config]
            query = metric_name + "{" + ",".join(label_list) + "}"
        else:
            query = metric_name
        _LOGGER.debug("Prometheus Query: %s", query)

        tasks = []
        while start < end:
            if start + chunk_seconds > end:
                chunk_seconds = end - start

            task = asyncio.ensure_future(
                self._session.get(
                    "{0}/query".format(self.api_url),
                    params={**{
                        "query": query + "[" + str(chunk_seconds) + "s" + "]",
                        "time": start + chunk_seconds,
                    }, **params},
                    verify=_config.ssl_verification
                )
            )
            tasks.append(task)

            start += chunk_seconds

        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code == 200:
                data += response.json()["data"]["result"]
            else:
                raise PrometheusApiClientException(
                    "HTTP Status Code {} ({!r})".format(
                        response.status_code, response.content)
                )
            if store_locally:
                # store it locally
                self._store_metric_values_local(
                    metric_name,
                    json.dumps(response.json()["data"]["result"]),
                    start + chunk_seconds,
                )

        return data
