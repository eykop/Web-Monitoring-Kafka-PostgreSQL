import time
import json
import logging
import sys

from kafka_helper.producer import Producer
from web_health_monitor.web_monitor import HealthMonitor

log = logging.getLogger("kafka_producer_script")

if __name__ == "__main__":
    producer = Producer("192.168.99.100:9092", "foobar")

    producer.connect()
    if not producer.connected:
        log.error("producer is not connected to Kafka server, existing ...")
        sys.exit(1)

    health_monitor = HealthMonitor("https://www.yahoo.com", "get", "(yahoo).+")
    while True:
        message = health_monitor.check()
        from pprint import  pprint
        print("------------------------------")
        pprint(message)
        ret = producer.send(json.dumps(message))
        print(ret)
        print("------------------------------")
        time.sleep(10)


