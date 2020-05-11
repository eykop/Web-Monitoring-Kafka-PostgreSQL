"""helper module for Kafka Producer"""

import logging
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError, NoBrokersAvailable, KafkaConfigurationError

from .kafka_helper import KafkaClientHelperBase

log = logging.getLogger("kafka_producer_helper")


class Producer(KafkaClientHelperBase):
    """Kafka Producer Client"""

    def __init__(self, host: str, topic: str, bulk_count: int, *args, **kwargs):
        super().__init__(host, topic, bulk_count)

    def connect(self) -> bool:
        """
        Connects to Kafka server
        :returns bool, True if connection is established, False otherwise.
        """
        try:
            # TODO add support for *args and **kwarsg
            self._client = KafkaProducer(bootstrap_servers=[self._host])
        except (KafkaConfigurationError, NoBrokersAvailable) as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._host, error)

        return self.connected

    def write(self, data: str):
        """
        Publishes a data message on Kafka server.
        """
        if self.connected:
            try:
                self._client.send(self._topic, data.encode())
            except KafkaTimeoutError as error:
                log.error("Error occurred when sending to Kafka server %s, for the following topic %s, details: %s",
                          self._host, self._topic, error)
        else:
            log.warning("Could not send data, producer is not connected to Kafka server.")

