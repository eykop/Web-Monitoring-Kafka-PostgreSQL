"""Module that help testing PostgreSQLClient"""
import unittest
from unittest import mock

import psycopg2

from kafka_postgres.definitions.keys import MessageJsonKeys
from kafka_postgres.postgresql_helper.exceptions import DataBaseOperationError
from ..postgresql_helper import PostgreSqlClient


class PostgreSQLClientTest(unittest.TestCase):
    """The PostgreSQLClient tester class"""

    def setUp(self) -> None:
        self._test_result = {
            MessageJsonKeys.MATCHES: 'yahoo.com"><link rel="preconnect" ',
            MessageJsonKeys.METHOD: 'get',
            MessageJsonKeys.PATTERN: "re.compile('(yahoo).+')",
            MessageJsonKeys.IS_PATTER_FOUND: True,
            MessageJsonKeys.RESPONSE_TIME_SECS: 0.317258,
            MessageJsonKeys.STATUS_CODE: 200,
            MessageJsonKeys.STATUS_CODE_OK: True,
            MessageJsonKeys.URL: 'https://www.yahoo.com'
        }

    def test_connection_success(self):
        """"Tests successful connection"""
        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = mock.Mock()
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name")
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)
        self.assertEqual(1, len(cursor_mock.execute.mock_calls))

    def test_connection_failed_db_not_found(self):
        """"Tests failed connection due to wrong database name """
        psycopg2.connect = mock.Mock()
        psycopg2.connect.side_effect = psycopg2.DatabaseError('FATAL:  database "nonexistingdb" does not exist')

        client = PostgreSqlClient("192.168.99.100", "nonexistingdb", "postgres", "mysecretpassword", "table_name")
        self.assertEqual(False, client.connect())
        self.assertEqual(False, client.connected)
        self.assertEqual(1, len(psycopg2.connect.mock_calls))

    def test_connection_failed_wrong_password(self):
        """"Tests failed connection due to wrong credentials"""
        psycopg2.connect = mock.Mock()
        psycopg2.connect.side_effect = psycopg2.DatabaseError(
            'FATAL:  password authentication failed for user "postgres"')

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "bas_password", "table_name")
        self.assertEqual(False, client.connect())
        self.assertEqual(False, client.connected)
        self.assertEqual(1, len(psycopg2.connect.mock_calls))

    def test_create_table_success(self):
        """Tests creation of db table for web monitoring successful"""

        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = mock.Mock()
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name2")
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)

        client.create_web_monitoring_table()
        self.assertEqual(2, len(cursor_mock.execute.mock_calls))

    def test_create_table_failed(self):
        """Tests creation of db table for web monitoring successful"""

        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = [mock.Mock(), psycopg2.errors.DuplicateTable]
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name2")
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)
        client.create_web_monitoring_table()

        # expected 2 since we assert the get version when connecting and the create table call
        self.assertEqual(2, len(cursor_mock.execute.mock_calls))

    def test_insert_web_monitor_result_to_db_success(self):
        """Tests insertion to table is success"""
        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = mock.Mock()
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name23")
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)

        client.insert_single_web_monitoring_result(self._test_result)
        self.assertEqual(2, len(cursor_mock.execute.mock_calls))

    def test_insert_web_monitor_result_to_db_failed(self):
        """Tests insertion to table is failed"""
        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = [mock.Mock(), DataBaseOperationError]
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name23")
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)
        with self.assertRaises(DataBaseOperationError):
            client.insert_single_web_monitoring_result(self._test_result)

    def test_insert_bulk_web_monitor_result_to_db_success(self):
        """Tests bulk insertion to table is success"""
        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = mock.Mock()
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name23", 2)
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)

        # we call twice - our bulk limit for this test is 2 , the insertion will happen in the second call.
        client.bulk_insert_monitoring_results(self._test_result)
        client.bulk_insert_monitoring_results(self._test_result)
        self.assertEqual(2, len(cursor_mock.execute.mock_calls))

    def test_insert_bulk_web_monitor_result_to_db_failed(self):
        """Tests bulk insertion to table is failed"""
        # we build mock from bottom to up
        cursor_mock = mock.Mock()
        cursor_mock.execute.side_effect = [mock.Mock(), DataBaseOperationError]
        cursor_mock.fetchone = mock.Mock()
        cursor_mock.fetchone.return_value = "Some PSQL version string"

        connect_mock = mock.Mock()
        connect_mock.cursor.return_value = cursor_mock

        psycopg2.connect = mock.Mock()
        psycopg2.connect.return_value = connect_mock

        client = PostgreSqlClient("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword", "table_name23", 2)
        self.assertEqual(True, client.connect())
        self.assertEqual(True, client.connected)

        # first does not trigger - our bulk limit for this test is 2
        client.bulk_insert_monitoring_results(self._test_result)

        with self.assertRaises(DataBaseOperationError):
            client.bulk_insert_monitoring_results(self._test_result)


if __name__ == '__main__':
    unittest.main()
