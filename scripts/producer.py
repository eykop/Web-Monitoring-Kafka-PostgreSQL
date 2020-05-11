import argparse
import os
import logging

from kafka_postgres.settings import settings
from kafka_postgres.settings.exceptions import ConfigurationException
from scripts.web_check import start_web_monitoring_website_checking

log = logging.getLogger("kafka_postgresql_demo")

# Configure logging
from kafka_postgres.settings.logger import logging_config # noqa # pylint:disable=unused-import

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
        start_web_monitoring_website_checking(kafka_config, web_monitor_config)
    except ConfigurationException as error:
        log.error("An error occurred, %s", error)






