"""helper module for Kafka Consumer"""
import logging
from typing import Callable
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaConfigurationError

from .kafka_helper import KafkaClientHelperBase

log = logging.getLogger("kafka_consumer_helper")


class Consumer(KafkaClientHelperBase):
    """Kafka Consumer Client"""

    def __init__(self, host: str, topic: str, bulk_count: int, *args, **kwargs):
        super().__init__(host, topic, bulk_count)

    def connect(self) -> bool:
        """
        Connects to Kafka server
        :returns bool, True if connection is established, False otherwise.
        """
        # TODO add support for *args and **kwarsg
        try:
            self._client = KafkaConsumer(self._topic, bootstrap_servers=[self._host],
                                         auto_offset_reset='earliest')
        except (KafkaConfigurationError, NoBrokersAvailable) as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._host, error)

        return self.connected

    def read(self, message_handler: Callable[[str], None]):
        """
        read all messages from the consumer, this function will wait(blocks) until
        there are new messages to read if the consumer has read all existing messages from Kafka.
        :param message_handler: lambda function to handle the read message, takes one argument and returns None.
        """
        for message in self._client:
            message_handler(message)



