import json
import logging
import argparse
import os
import sys
from json import JSONDecodeError

from kafka_postgres.kafka_helper.consumer import Consumer
from kafka_postgres.postgresql_helper.exceptions import DataBaseOperationError
from kafka_postgres.postgresql_helper.postgresql_helper import PostgreSqlClient
from kafka_postgres.settings import settings
from kafka_postgres.settings.exceptions import ConfigurationException

log = logging.getLogger("kafka_postgresql_demo")
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


def start_kafka_consumer(kafka_config: dict, postgresql_config: dict):
    try:
        try:
            consumer = Consumer(**kafka_config)
            client = PostgreSqlClient(**postgresql_config)
        except KeyError as key_error:
            consumer.close()
            client.close()
            log.error("Configuration value missing from config file:  %s", key_error)

        def insert_to_tbl(data: str):
            log.debug("message: %s", data)
            try:
                json_data = json.loads(data)
                # json_data["pattern"] = json_data["pattern"].replace("\"", "\'")
                json_data["pattern"] = '%s'%json_data["pattern"].replace("'", "\"")
                client.bulk_insert_monitoring_results(json_data)
            except JSONDecodeError as json_error:
                log.error("Failed to decode message to json: %s.", json_error)

        if consumer.connect() and client.connect():
            log.info("Successfully connected to Kafka, starting to consume an process messages. ")
            consumer.read(message_handler=lambda consumer_record: insert_to_tbl(consumer_record.value))

    except DataBaseOperationError as db_error:
        log.info("A Database operation error occurred: %s, will stop run.", db_error)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n")
        print("Received Ctrl-C, closing connection and existing...")
        consumer.close()
        client.close()
        sys.exit(0)


if __name__ == "__main__":
    """
    Entry point of the script  
    """

    # define command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="configuration ini file path.")

    # parse command arguments and read config file
    args = parser.parse_args()
    try:
        config_file_path = os.path.abspath(args.config)
        log.debug("config file argument value: '%s'", config_file_path)

        postgresql_config = settings.get_config(config_file_path, "postgresql")
        kafka_config = settings.get_config(config_file_path, "kafka")

        # TODO - do not print password to screen
        log.debug("postgresql_config %s", postgresql_config)
        log.debug("kafka_config %s", kafka_config)

        # start reporting to postgres db while consuming form Kafka
        start_kafka_consumer(kafka_config, postgresql_config)
    except ConfigurationException as error:
        log.error("An error occurred, %s", error)

