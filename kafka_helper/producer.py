"""helper module for Kafka Producer"""

import logging
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError, NoBrokersAvailable, KafkaConfigurationError

from .kafka_helper import KafkaHelperBase

log = logging.getLogger("kafka_producer_helper")


class Producer(KafkaHelperBase):
    """Kafka Producer Client"""

    def __init__(self, server_address: str, topic: str):
        super().__init__(server_address, topic)
        self._producer = None

    def connect(self) -> bool:
        """
        Connects to Kafka server
        :returns bool, True if connection is established, False otherwise.
        """
        try:
            self._producer = KafkaProducer(bootstrap_servers=[self._server_address])
        except (KafkaConfigurationError, NoBrokersAvailable) as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._server_address, error)

        return self.connected

    @property
    def connected(self):
        """Check if consumer is connected or not, returns matching connected status as boolean"""
        return self._producer is not None

    def send(self, data: str):
        """
        Publishes a data message on Kafka server.
        """
        if self.connected:
            try:
                self._producer.send(self._topic, data.encode())
                self._producer.flush()
            except KafkaTimeoutError as error:
                log.error("Error occurred when sending to Kafka server %s, for the following topic %s, details: %s",
                          self._server_address, self._topic, error)
        else:
            log.warning("Could not send data, producer is not connected to Kafka server.")