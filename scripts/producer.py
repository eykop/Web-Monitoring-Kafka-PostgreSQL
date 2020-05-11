import argparse
import os
import time
import json
import logging
import sys

from kafka_postgres.settings import settings
from kafka_postgres.kafka_helper.producer import Producer
from kafka_postgres.web_health_monitor.exceptions import WebMonitorException
from kafka_postgres.web_health_monitor.web_monitor import HealthMonitor
from kafka_postgres.settings.exceptions import ConfigurationException

log = logging.getLogger("kafka_postgresql_demo")

# Configure logging
from kafka_postgres.settings.logger import logging_config # noqa # pylint:disable=unused-import


def start_kafka_producer(kafka_config: dict, web_monitor_config: dict):

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

        web_monitor_config = settings.get_config(config_file_path, "web_monitor")
        kafka_config = settings.get_config(config_file_path, "kafka")

        # start reporting to postgres db while consuming form Kafka
        start_kafka_producer(kafka_config, web_monitor_config)
    except ConfigurationException as error:
        log.error("An error occurred, %s", error)






