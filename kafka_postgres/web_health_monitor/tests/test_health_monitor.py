import http
import unittest
import uuid
from unittest import mock
from datetime import timedelta

import requests

from ..web_monitor import HealthMonitor


class HealthMonitorTest(unittest.TestCase):

    def setUp(self) -> None:
        self._UUID4_REGEX = "[a-z0-9]{8}\-([a-z0-9]{4}\-){3}[a-z0-9]{8}"
        self._web_monitor = HealthMonitor("https://www.exafasfasfasfasfsafmple.com", "get", self._UUID4_REGEX)

    @mock.patch.object(requests, "request")
    def test_check_success_result(self, mock_get):
        """Tests sending a get request and getting the expected "success" results"""
        mock_response = mock.Mock()

        mock_response.status_code = http.HTTPStatus.OK
        mock_response.content = f" some response text {str(uuid.uuid4())} additional response text".encode()
        mock_response.elapsed = timedelta(microseconds=300)
        mock_get.return_value = mock_response
        result = self._web_monitor.check()
        self.assertEqual(mock_response.status_code, result["status_code"])
        self.assertEqual(mock_response.elapsed.total_seconds(), result["response_time_in_sec"])
        self.assertEqual(True, result["pattern_found"])

    @mock.patch.object(requests, "request")
    def test_check_filed_with_pattern_not_found(self, mock_get):
        """Tests sending a get request and getting the expected failed results"""
        mock_response = mock.Mock()
        mock_response.status_code = http.HTTPStatus.OK
        mock_response.content = f" some response text, additional response text".encode()
        mock_response.elapsed = timedelta(microseconds=300)
        mock_get.return_value = mock_response
        result = self._web_monitor.check()
        self.assertEqual(mock_response.status_code, result["status_code"])
        self.assertEqual(mock_response.elapsed.total_seconds(), result["response_time_in_sec"])
        self.assertEqual(False, result["pattern_found"])

    @mock.patch.object(requests, "request")
    def test_check_netwrok_error(self, mock_get):
        """Test network error case, we catch the error and do not crash"""
        mock_get.side_effect = requests.exceptions.ConnectionError
        result = self._web_monitor.check()
        # dummy timedelta value just for the test
        self.assertEqual(http.HTTPStatus.NOT_FOUND, result["status_code"])
        self.assertGreater(timedelta(seconds=100).total_seconds(), result["response_time_in_sec"])
        self.assertEqual(False, result["pattern_found"])




if __name__ == '__main__':
    unittest.main()
