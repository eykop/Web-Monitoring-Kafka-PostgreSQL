"""Helper module for kafka producer and consumer implemenations"""

from abc import ABC, abstractmethod


class KafkaHelperBase(ABC):
    """Base class for Kafka consumer and producer"""

    def __init__(self, server_address: str, topic: str):
        """
        Initializes Kafka Object with required server address and topic.
        :param server_address: the server to connect to.
        :param topic: the topic to subscribe.
        """
        self._server_address = server_address
        self._topic = topic

    def connect(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError


