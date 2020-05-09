import argparse
import os
import time
import json
import logging
import sys

from kafka_postgres.settings import settings
from kafka_postgres.kafka_helper.producer import Producer
from kafka_postgres.settings.exceptions import ConfigurationFileNotFoundException
from kafka_postgres.web_health_monitor.web_monitor import HealthMonitor

log = logging.getLogger("kafka_producer_script")
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)


def start_kafka_producer(kafka_config: dict, web_monitor_config: dict):
    try:
        try:
            producer = Producer(**kafka_config)
        except KeyError as kw_error:
            producer.close()
            log.error("Configuration value missing from config file:  %s", kw_error)

        if producer.connect():
            log.info("Successfully connected to Kafka, starting to consume an process messages. ")
        if not producer.connected:
            log.error("producer is not connected to Kafka server, existing ...")
            sys.exit(1)

        health_monitor = HealthMonitor(**web_monitor_config)

        while True:
            data = health_monitor.check()
            log.debug("message: %s", json.dumps(data))
            producer.send(json.dumps(data))

            # TODO flush on given bulk count and not every message!
            #  plus this private and  should not be done from here!
            producer._producer.flush()

            # TODO sleep should be configrable similar as flush bulk count
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n")
        print("Recived Ctrl-C, closing connection and existing...")
        producer.close()
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
    config_file_path = os.path.abspath(args.config)

    try:
        config_file_path = os.path.abspath(args.config)
        log.debug("config file argument value: '%s'", config_file_path)

        web_monitor_config = settings.get_config(config_file_path, "web_monitor")
        kafka_config = settings.get_config(config_file_path, "kafka")

        # TODO - do not print password to screen
        log.debug("web_monitor_config %s", web_monitor_config)
        log.debug("kafka_config %s", kafka_config)

        # start reporting to postgres db while consuming form Kafka
        start_kafka_producer(kafka_config, web_monitor_config)
    except ConfigurationFileNotFoundException as error:
        log.error("An error occurred, %s", error)






