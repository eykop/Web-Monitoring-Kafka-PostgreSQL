import logging
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError, NoBrokersAvailable

from .kafka_helper import KafkaHelperBase

log = logging.getLogger("kafka_producer_helper")


class Producer(KafkaHelperBase):

    def __init__(self, server_address: str, topic: str):
        super().__init__(server_address, topic)
        self._producer = None

    def connect(self):
        try:
            self._producer = KafkaProducer(bootstrap_servers=[self._server_address])
        except NoBrokersAvailable as error:
            log.error("Error occurred when connecting to Kafka server %s, details: %s",
                      self._server_address, error)

    @property
    def connected(self):
        return self._producer is not None

    def send(self, data: str):
        if self.connected:
            try:
                self._producer.send(self._topic, data.encode())
                self._producer.flush()
            except KafkaTimeoutError as error:
                log.error("Error occurred when sending to Kafka server %s, for the following topic %s, details: %s",
                          self._server_address, self._topic, error)
        else:
            log.warning("Could not send data, producer is not connected to Kafka server.")