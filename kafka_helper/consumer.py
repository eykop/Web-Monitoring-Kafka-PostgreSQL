import logging
from typing import Callable
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from .kafka_helper import KafkaHelperBase

log = logging.getLogger("kafka_producer_helper")


class Consumer(KafkaHelperBase):

    def __init__(self, server_address: str, topic: str):
        super().__init__(server_address, topic)
        self._consumer = None

    def connect(self):
        # TODO add support for *args and **kwarsg
        try:
            self._consumer = KafkaConsumer(bootstrap_servers=[self._server_address], auto_offset_reset='earliest')
            self._consumer.subscribe([self._topic])
        except NoBrokersAvailable as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._server_address, error)

    @property
    def connected(self):
        return self._consumer is not None

    def read(self, message_handler: Callable[[str], None]):
        for msg in self._consumer:
            message_handler(msg)
