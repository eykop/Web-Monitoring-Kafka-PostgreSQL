"""Module to to monitor health of a given website"""
import re
import requests
import urllib3
from datetime import datetime
from http import HTTPStatus

from kafka_postgres.definitions.keys import MessageJsonKeys
from kafka_postgres.web_health_monitor.exceptions import WebMonitorException


class HealthMonitor:
    """HealthMonitor provide services to monitor status of a website"""

    def __init__(self, url: str,
                 http_request_type: str = "get",
                 regex_to_verify: str = None,
                 http_success_status_code: HTTPStatus = HTTPStatus.OK,
                 monitor_interval_in_sec: int = 10):
        """
        Initialize HealthMonitor instance, it uses the provided arguments to perform the health check.

        :param url: the url of the website to monitor.
        :param http_request_type: the http request type.
        :param regex_to_verify: a regular expression to verify it appears on the http request response body.
        :param http_success_status_code: the http response status code to consider as success.
        :param monitor_interval_in_sec: interval to wait between checks.
        """
        self._url = url
        self._request_type = http_request_type
        self._success_status = http_success_status_code
        self._raw_regex = regex_to_verify
        self._verification_regex = re.compile(regex_to_verify)
        self._sampling_interval = int(monitor_interval_in_sec)

    def check(self, *params, **kwargs) -> dict:
        """
        Performs the check request.
        :param params: (optional) Dictionary, list of tuples or bytes to send
        in the query string.
        :param kwargs:
        :return: dict of (status_code, response_time, pattern_found), where:
                    status_code: an int representing the response status code.
                    response_time: a timedelta the for response time.
                    pattern_found:  a bool reflects if the verification regex was match in the response body or not.
        """
        match_string = ""
        try:
            before_request = datetime.now()
            response = requests.request(self._request_type, self._url, params=params, **kwargs)
            status_code = response.status_code
            content = response.content.decode('utf-8')
            response_time = response.elapsed.total_seconds()

            match = self._verification_regex.search(content)
            has_pattern_in_response_body = match is not None
            if has_pattern_in_response_body:
                match_string = match.group()

        except (requests.exceptions.ConnectionError, urllib3.exceptions.NewConnectionError) as err:
            time_delta = datetime.now() - before_request
            status_code = HTTPStatus.NOT_FOUND
            response_time = time_delta.total_seconds()
            has_pattern_in_response_body = False
            raise WebMonitorException(err)

        return {
            MessageJsonKeys.STATUS_CODE: status_code,
            MessageJsonKeys.STATUS_CODE_OK:  status_code == HTTPStatus.OK,
            MessageJsonKeys.URL: self._url,
            MessageJsonKeys.METHOD: self._request_type,
            MessageJsonKeys.PATTERN: self._raw_regex,
            MessageJsonKeys.MATCHES: match_string,
            MessageJsonKeys.RESPONSE_TIME_SECS: response_time,
            MessageJsonKeys.IS_PATTER_FOUND: has_pattern_in_response_body
        }

    @property
    def monitor_interval_in_sec(self) -> int:
        """Returns the monitor interval in seconds"""
        return self._sampling_interval


