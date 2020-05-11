"""Helper module for kafka producer and consumer implementations"""

from abc import ABC, abstractmethod


class KafkaClientHelperBase(ABC):
    """Base class for Kafka consumer and producer"""

    def __init__(self, host: str, topic: str, bulk_count: int):
        """
        Initializes Kafka Object with required server address and topic.
        :param host: the server to connect to.
        :param topic: the topic to subscribe.
        """
        self._host = host
        self._topic = topic
        self._bulk_count = int(bulk_count)
        self._client = None

    @abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError

    def close(self):
        if self.connected:
            self._client.close()

    @property
    def connected(self) -> bool:
        """Check if client is connected or not, returns matching connected status as boolean"""
        return self._client is not None

    @property
    def bulk_count(self):
        return self._bulk_count

    @property
    def client(self):
        return self._client
