import logging
from logging.config import dictConfig

logging_config = dict(
    version=1,
    formatters={
        'f': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
    },
    root={
        'handlers': ['h'],
        'level': logging.DEBUG,
    },
    loggers={
        'kafka_postgresql_demo':{
            "level": "DEBUG"
        },
        'postgresql_client_helper':{
            "level": "DEBUG"
        },
        'kafka_consumer_helper':{
            "level": "DEBUG"
        },
        'kafka_producer_helper':{
            "level": "DEBUG"
        },
        'kafka.metrics.metrics':{
            "level": "INFO"
        },
        'kafka.conn':{
            "level": "INFO"
        },
        'kafka.client':{
            "level": "INFO"
        },


    }
)
dictConfig(logging_config)
