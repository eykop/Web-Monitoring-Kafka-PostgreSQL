from pprint import pprint
from kafka_helper.consumer import Consumer

if __name__ == "__main__":
    consumer = Consumer("192.168.99.100:9092", "foobar")
    consumer.connect()
    print("------------------------------")
    consumer.read(message_handler=lambda consumer_record: pprint(consumer_record.value))
    print("------------------------------")


