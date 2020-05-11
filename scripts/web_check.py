import json
import sys
import time
import logging
from json.decoder import JSONDecodeError

from kafka_postgres.definitions.keys import MessageJsonKeys
from kafka_postgres.kafka_helper.consumer import Consumer
from kafka_postgres.kafka_helper.producer import Producer
from kafka_postgres.postgresql_helper.exceptions import DataBaseOperationError
from kafka_postgres.postgresql_helper.postgresql_helper import PostgreSqlClient
from kafka_postgres.web_health_monitor.exceptions import WebMonitorException
from kafka_postgres.web_health_monitor.web_monitor import HealthMonitor


log = logging.getLogger("kafka_postgresql_demo")


def start_web_monitoring_database_reporting(kafka_config: dict, postgresql_config: dict) -> None:
    """
    Starts the Web monitoring results to database part.
    It will starts the Kafka consumer and PostgreSQL clients so it can consume new results and report them to
    the data base.
    :param kafka_config: the Kafka configuration (as from config file).
    :param postgresql_config: the PostgreSQL configuration (as from config file).
    """
    try:
        consumer = Consumer(**kafka_config)
        db_client = PostgreSqlClient(**postgresql_config)

        messages_bulk = []

        def insert_to_table(data: str):
            """helper internal method to act as the lambda function for the consumer read"""

            log.debug("message: %s", data)
            try:
                json_data = json.loads(data)
                json_data["pattern"] = '%s'%json_data["pattern"].replace("'", "\"")
                messages_bulk.append(
                    (json_data[MessageJsonKeys.URL],
                     json_data[MessageJsonKeys.STATUS_CODE],
                     json_data[MessageJsonKeys.STATUS_CODE_OK],
                     json_data[MessageJsonKeys.RESPONSE_TIME_SECS],
                     json_data[MessageJsonKeys.METHOD],
                     json_data[MessageJsonKeys.IS_PATTERN_FOUND],
                     json_data[MessageJsonKeys.PATTERN],
                     json_data[MessageJsonKeys.MATCHES][:255])
                )
                if len(messages_bulk) >= consumer.bulk_count:
                    db_client.bulk_insert_monitoring_results(messages_bulk)
                    messages_bulk.clear()
                else:
                    log.debug(
                        "Bulk insert limit to web monitoring, not reached yet current %d - required %d .",
                        len(messages_bulk),
                        consumer.bulk_count)

            except JSONDecodeError as json_error:
                log.error("Failed to decode message to json: %s.", json_error)

        if consumer.connect() and db_client.connect():
            log.info("Successfully connected to Kafka, starting to consume an process messages. ")
            consumer.read(message_handler=lambda consumer_record: insert_to_table(consumer_record.value))

    except KeyError as key_error:
        consumer.close()
        db_client.close()
        log.error("Configuration value missing from config file:  %s", key_error)
        sys.exit(1)

    except DataBaseOperationError as db_error:
        log.info("A Database operation error occurred: %s, will stop run.", db_error)
        sys.exit(1)

    except KeyboardInterrupt:
        log.info("Received Ctrl-C, closing connection and existing...")
        consumer.close()
        db_client.close()
        sys.exit(0)


def start_web_monitoring_website_checking(kafka_config: dict, web_monitor_config: dict) -> None:
    """
    Starts the Web monitoring actual checking.
    It will starts the Kafka producer and WebMonitor clients so it can perform new check and produce new the check
    results into Kakfa topic.
    :param kafka_config: the Kafka configuration (as from config file).
    :param web_monitor_config: the Web Monitoring configuration (as from config file).
    """

    try:
        producer = Producer(**kafka_config)

        if producer.connect():
            log.info("Successfully connected to Kafka, starting to consume and process messages.")
            health_monitor = HealthMonitor(**web_monitor_config)
            check_counter = 0
            while True:
                data = health_monitor.check()
                check_counter += 1
                log.debug("message: %s", json.dumps(data))
                producer.write(json.dumps(data))

                if check_counter >= producer.bulk_count:
                    producer.client.flush()
                    check_counter = 0

                time.sleep(health_monitor.monitor_interval_in_sec)

    except KeyError as kw_error:
        producer.close()
        log.error("Configuration value missing from config file:  %s", kw_error)
        sys.exit(1)

    except WebMonitorException as wm_error:
        producer.close()
        log.error("An Error occurred during web monitoring, details: %s", wm_error)
        sys.exit(1)

    except KeyboardInterrupt:
        log.info("Received Ctrl-C, closing connection and existing...")
        producer.close()
        sys.exit(0)