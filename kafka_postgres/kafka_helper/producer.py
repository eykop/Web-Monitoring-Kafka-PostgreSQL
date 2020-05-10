"""helper module for Kafka Producer"""

import logging
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError, NoBrokersAvailable, KafkaConfigurationError

from .kafka_helper import KafkaHelperBase

log = logging.getLogger("kafka_producer_helper")


class Producer(KafkaHelperBase):
    """Kafka Producer Client"""

    def __init__(self, host: str, topic: str, bulk_count: int, *args, **kwargs):
        super().__init__(host, topic)
        self._client = None
        self._bulk_count = int(bulk_count)

    def connect(self) -> bool:
        """
        Connects to Kafka server
        :returns bool, True if connection is established, False otherwise.
        """
        try:
            self._client = KafkaProducer(bootstrap_servers=[self._host])
        except (KafkaConfigurationError, NoBrokersAvailable) as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._host, error)

        return self.connected

    @property
    def connected(self):
        """Check if consumer is connected or not, returns matching connected status as boolean"""
        return self._client is not None

    def send(self, data: str):
        """
        Publishes a data message on Kafka server.
        """
        if self.connected:
            try:
                self._client.send(self._topic, data.encode())
                # TODO flush blocks should remove from here and use with bulk
                self._client.flush()
            except KafkaTimeoutError as error:
                log.error("Error occurred when sending to Kafka server %s, for the following topic %s, details: %s",
                          self._host, self._topic, error)
        else:
            log.warning("Could not send data, producer is not connected to Kafka server.")

    def close(self):
        if self.connected:
            self._client.close()

    @property
    def client(self):
        return self._client

    @property
    def bulk_count(self):
        return self._bulk_count
