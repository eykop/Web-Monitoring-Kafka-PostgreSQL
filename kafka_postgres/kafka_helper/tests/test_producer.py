import unittest
from unittest import mock

from kafka.errors import NoBrokersAvailable

from ..producer import Producer


class ProducerTest(unittest.TestCase):

    @mock.patch("kafka_helper.producer.KafkaProducer")
    def test_failed_to_connect(self, mock_kafka_producer):
        mock_kafka_producer.side_effect = NoBrokersAvailable
        kf_producer = Producer("192.168.99.100:9092", "topic")
        self.assertEqual(False, kf_producer.connect())
        self.assertEqual(False, kf_producer.connected)

    @mock.patch("kafka_helper.consumer.KafkaConsumer")
    def test_connected_successfully(self, mock_kafka_producer):
        mock_kafka_producer.return_value = mock.Mock()
        kf_producer = Producer("192.168.99.100:9092", "topic")
        self.assertEqual(True, kf_producer.connect())
        self.assertEqual(True, kf_producer.connected)




if __name__ == '__main__':
    unittest.main()
