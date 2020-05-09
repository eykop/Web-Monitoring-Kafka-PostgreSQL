import unittest

from ..postgresql_helper import PostgreSqlClient
class PostgreSQLClientTest(unittest.TestCase):

    def test_connection_success(self):
        """"Tests successful connection"""
        client = PostgreSqlClient()
        client.connect("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword")
        self.assertEqual(True, client.connected)

    def test_connection_failed_db_not_found(self):
        """"Tests failed connection due to wrong database name """
        client = PostgreSqlClient()
        client.connect("192.168.99.100", "nonexistingdb", "postgres", "mysecretpassword")
        self.assertEqual(False, client.connected)

    def test_connection_failed_wrong_password(self):
        """"Tests failed connection due to wrong credentials"""
        client = PostgreSqlClient()
        client.connect("192.168.99.100", "mydb", "postgres", "bas_password")
        self.assertEqual(False, client.connected)

    def test_create_table_success(self):
        """Tests creation of db table for web monitoring successful"""
        client = PostgreSqlClient()
        client.connect("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword")
        self.assertEqual(True, client.connected)
        client.create_web_monitoring_table(website_name="yahoo")

    def test_insert_web_monitor_result_to_db(self):
        client = PostgreSqlClient()
        client.connect("192.168.99.100", "web_monitoring", "postgres", "mysecretpassword")
        self.assertEqual(True, client.connected)
        test_result = {
            'matches': 'yahoo.com"><link rel="preconnect" '
                       'href="//csc.beap.bc.yahoo.com"><link rel="dns-prefetch" '
                       'href="//geo.yahoo.com"><link rel="preconnect" '
                       'href="//geo.yahoo.com"><link rel="dns-prefetch" '
                       'href="//comet.yahoo.com"><link rel="preconnect" '
                       'href="//comet.yahoo.com"><link rel="dns-prefetch" '
                       'href="//video-api.yql.yahoo.com"><link rel="preconnect" '
                       'href="//video-api.yql.yahoo.com">    <meta '
                       'http-equiv="Content-Type" content="text/html; charset=utf-8">',
            'method': 'get',
            'pattern': "re.compile('(yahoo).+')",
            'pattern_found': True,
            'response_time_in_sec': 0.317258,
            'status_code': 200,
            'url': 'https://www.yahoo.com'
        }
        client.insert_web_monitoring_result("yahoo", test_result)







if __name__ == '__main__':
    unittest.main()
