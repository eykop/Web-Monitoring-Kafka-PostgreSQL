import unittest
from unittest import mock

from kafka.errors import NoBrokersAvailable

from ..consumer import Consumer


class ConsumerTest(unittest.TestCase):

    @mock.patch("kafka_postgres.kafka_helper.consumer.KafkaConsumer")
    def test_failed_to_connect(self, mock_kafka_consumer):
        """Tests failure on connecting"""
        mock_kafka_consumer.side_effect = NoBrokersAvailable
        kf_consumer = Consumer("192.168.99.100:9092", "topic", 10, "groupid1")
        self.assertEqual(False,kf_consumer.connect())
        self.assertEqual(False, kf_consumer.connected)

    @mock.patch("kafka_postgres.kafka_helper.consumer.KafkaConsumer")
    def test_connected_successfully(self, mock_kafka_consumer):
        """Tests success on connecting"""
        mock_kafka_consumer.return_value = mock.Mock()
        kf_consumer = Consumer("192.168.99.100:9092", "topic", 10, "groupid1")
        self.assertEqual(True, kf_consumer.connect())
        self.assertEqual(True, kf_consumer.connected)

    @mock.patch("kafka_postgres.kafka_helper.consumer.KafkaConsumer")
    def test_read_messages(self, mock_kafka_consumer):
        """
        Tests reading of messages from consumer, this test does not really test reading from a stream,
        but rather just checking messages are returned from read and they can be processed by the provided
         callable lambda function.
        """
        def dummy_mocking_consumer(topic, bootstrap_servers, auto_offset_reset, group_id):
            """dummy mocked consumer, it just returns a list of messages!"""
            return [{"message": 1}]*10

        mock_kafka_consumer.side_effect = dummy_mocking_consumer
        kf_consumer = Consumer("192.168.99.100:9092", "topic", 10, "groupid1")
        self.assertEqual(True, kf_consumer.connect())
        self.assertEqual(True, kf_consumer.connected)
        kf_consumer.read(lambda msg: self.assertDictEqual({"message": 1}, msg))



if __name__ == '__main__':
    unittest.main()
