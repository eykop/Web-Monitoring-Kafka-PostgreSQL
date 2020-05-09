"""
Module that simplify few calls to PostgreSQL

Acknowledgement:
some of the code is based on the tutorial form https://www.postgresqltutorial.com/postgresql-python
"""
import psycopg2
import logging

log = logging.getLogger("postgresql_client_helper")


class PostgreSqlClient:
    """PostGreSQL simple client"""

    def __init__(self):
        # the posgresql connection
        self._connection = None

    def connect(self, host: str, database: str, user: str, password: str) -> bool:
        """
        Initialize the client and connects to PostgreSQL server.
        :param host: database server address e.g., localhost or an IP address
        :param database: the name of the database that you want to connect.
        :param user: the username used to authenticate.
        :param password: password used to authenticate.
        :returns bool: True if connection is established , False otherwise.
        """
        try:

            self._connection = psycopg2.connect(host=host, database=database, user=user, password=password)

            # create a cursor
            self._cursor = self._connection.cursor()

            # execute a statement
            self._cursor.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = self._cursor.fetchone()
            log.debug('PostgreSQL database version: %s', db_version)

            log.info("Successfully connected to PosgreSQL server %s, version %s", host, db_version)

        except (Exception, psycopg2.DatabaseError) as error:
            log.error("Error occurred when connecting to PostgreSQL server %s, details: %s",
                      host, error)

        return self.connected

    @property
    def connected(self) -> bool:
        """Check if postgresql client is connected or not, returns matching connected status as boolean"""
        return self._connection is not None

    def create_web_monitoring_data_base(self, data_base_name):
        pass

    def create_web_monitoring_table(self, website_name):
        command = (
            f"""
            CREATE TABLE {website_name} (
                request_id SERIAL PRIMARY KEY,
                url VARCHAR(255) NOT NULL,
                status_code NUMERIC ,
                status_ok boolean NOT NULL,
                response_time NUMERIC ,
                check_metHod VARCHAR(15) NOT NULL,
                pattern_matched boolean NOT NULL,
                requested_pattern VARCHAR(255) NOT NULL,
                matched_text VARCHAR(255) NOT NULL
            )
            """)
        try:
            self.execute_query(command)
            log.info("Sql table %s created.", website_name)
        except psycopg2.errors.DuplicateTable as error:
            log.info("Sql table %s exists.", website_name)

    def insert_web_monitoring_result(self, table: str, result: dict):
        """ insert a new webcheck into the vendors table """
        sql = f"""INSERT INTO {table}(url, status_code, status_ok, response_time, check_method, 
                    pattern_matched, requested_pattern, matched_text) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) 
                  RETURNING request_id;"""
        try:
            self._cursor.execute(sql,
                                 (result["url"],
                                  result["status_code"],
                                  result["status_code"] != 200,
                                  result["response_time_in_sec"],
                                  result["method"],
                                  result["pattern_found"],
                                  result["pattern"],
                                  result["matches"][:255])
                                 )
            self._connection.commit()
        except (psycopg2.errors.DatatypeMismatch,
                psycopg2.errors.InvalidTextRepresentation,
                psycopg2.errors.UndefinedColumn,
                psycopg2.errors.NotNullViolation,
                TypeError) as error:
            log.error("An error occurred during insertion of result to data base table table %s , details: %s",
                      table, error)

    def execute_query(self, query):
        self._cursor.execute(query)
        # commit the changes
        self._connection.commit()

    def close(self):
        """Closes sql server connection"""
        if self._cursor:
            self._cursor.close()

        if self._connection:
            self._connection.close()

