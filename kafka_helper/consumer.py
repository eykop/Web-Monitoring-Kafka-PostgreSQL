"""helper module for Kafka Consumer"""
import logging
from typing import Callable
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaConfigurationError

from .kafka_helper import KafkaHelperBase

log = logging.getLogger("kafka_consumer_helper")


class Consumer(KafkaHelperBase):
    """Kafka Consumer Client"""

    def __init__(self, server_address: str, topic: str):
        super().__init__(server_address, topic)
        self._consumer = None

    def connect(self) -> bool:
        """
        Connects to Kafka server
        :returns bool, True if connection is established, False otherwise.
        """
        # TODO add support for *args and **kwarsg
        try:
            self._consumer = KafkaConsumer(self._topic, bootstrap_servers=[self._server_address],
                                           auto_offset_reset='earliest')
        except (KafkaConfigurationError, NoBrokersAvailable) as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._server_address, error)

        return self.connected

    @property
    def connected(self) -> bool:
        """Check if consumer is connected or not, returns matching connected status as boolean"""
        return self._consumer is not None

    def read(self, message_handler: Callable[[str], None]):
        """
        read all messages from the consumer, this function will wait(blocks) until
        there are new messages to read if the consumer has read all existing messages from Kafka.
        :param message_handler: lambda function to handle the read message, takes one argument and returns None.
        """
        for msg in self._consumer:
            message_handler(msg)

