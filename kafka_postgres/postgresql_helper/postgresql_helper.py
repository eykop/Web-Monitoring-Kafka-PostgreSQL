"""
Module that simplify few calls to PostgreSQL

Acknowledgement:
some of the code is based on the tutorial form https://www.postgresqltutorial.com/postgresql-python
"""
import psycopg2
import logging

from kafka_postgres.postgresql_helper.exceptions import DataBaseOperationError
from kafka_postgres.definitions.keys import MessageJsonKeys

log = logging.getLogger("postgresql_client_helper")


class PostgreSqlClient:
    """PostGreSQL simple client"""

    def __init__(self,
                 host: str,
                 database: str,
                 user: str,
                 password: str,
                 table_name: str):
        """
        Initialize the client.
        :param host: database server address e.g., localhost or an IP address
        :param database: the name of the database that you want to connect.
        :param user: the username used to authenticate.
        :param password: password used to authenticate.
        :param table_name: the db table name to perform the queries on.
        """
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._table_name = table_name
        self._connection = None
        self._cursor = None

    def connect(self) -> bool:
        """
        Connects to PostgreSQL server.
        :returns bool: True if connection is established , False otherwise.
        """
        try:

            self._connection = psycopg2.connect(host=self._host,
                                                database=self._database,
                                                user=self._user,
                                                password=self._password)

            # create a cursor
            self._cursor = self._connection.cursor()

            # execute a statement
            self._cursor.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = self._cursor.fetchone()
            log.debug('PostgreSQL database version: %s', db_version)

            log.info("Successfully connected to PostgreSQL server %s, version %s", self._host, db_version)

        except (Exception, psycopg2.DatabaseError) as error:
            log.error("Error occurred when connecting to PostgreSQL server %s, details: %s",
                      self._host, error)

        return self.connected

    @property
    def connected(self) -> bool:
        """Check if PostgreSQL client is connected or not, returns matching connected status as boolean"""
        return self._connection is not None

    def create_web_monitoring_table(self):
        command = (
            f"""
            CREATE TABLE {self._table_name} (
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
            log.info("Sql table %s created.", self._table_name)
        except psycopg2.errors.DuplicateTable as error:
            log.warning("Sql table %s exists: %s.", self._table_name, error)

    def bulk_insert_monitoring_results(self, results: list):
        """Inserts a bulk of results to db table at once if a predefined bulk count is reached.
        :param results: the wbe check results list.
        """
        current_list_size = len(results)

        sql = f"""INSERT INTO {self._table_name}(url, status_code, status_ok, response_time, check_method, 
                  pattern_matched, requested_pattern, matched_text) VALUES %s;"""

        var_string = ', '.join(['%s'] * current_list_size)
        sql = sql % var_string
        try:

            self._cursor.execute(sql, tuple(results))
            self._connection.commit()
        except (psycopg2.errors.DatatypeMismatch,
                psycopg2.errors.SyntaxError,
                psycopg2.errors.InvalidTextRepresentation,
                psycopg2.errors.UndefinedColumn,
                psycopg2.errors.NotNullViolation,
                TypeError) as error:
            log.error("An error occurred during insertion of result to data base table table %s , details: %s",
                      self._table_name, error)
            raise DataBaseOperationError(error)

    def insert_single_web_monitoring_result(self, result: dict):
        """ insert a new web check into the vendors table """
        sql = f"""INSERT INTO {self._table_name}(url, status_code, status_ok, response_time, check_method, 
                    pattern_matched, requested_pattern, matched_text) VALUES(%s,%s,%s,%s,%s,%s,%s,%s) 
                  RETURNING request_id;"""
        try:
            self._cursor.execute(sql,
                                 (result[MessageJsonKeys.URL],
                                  result[MessageJsonKeys.STATUS_CODE],
                                  result[MessageJsonKeys.STATUS_CODE] != 200,
                                  result[MessageJsonKeys.RESPONSE_TIME_SECS],
                                  result[MessageJsonKeys.METHOD],
                                  result[MessageJsonKeys.IS_PATTER_FOUND],
                                  result[MessageJsonKeys.PATTERN],
                                  result[MessageJsonKeys.MATCHES][:255])
                                 )
            self._connection.commit()
        except (psycopg2.errors.DatatypeMismatch,
                psycopg2.errors.InvalidTextRepresentation,
                psycopg2.errors.UndefinedColumn,
                psycopg2.errors.NotNullViolation,
                psycopg2.errors.UndefinedTable,
                psycopg2.errors.SyntaxError,
                TypeError) as error:
            log.error("An error occurred during insertion of result to data base table table %s , details: %s",
                      self._table_name, error)
            raise DataBaseOperationError(error)

    def execute_query(self, query):
        """
        Executes an sql query
        :param query: the query to execute
        """
        self._cursor.execute(query)
        # commit the changes
        self._connection.commit()

    def close(self):
        """Closes sql server connection"""
        if self._cursor:
            self._cursor.close()

        if self._connection:
            self._connection.close()

