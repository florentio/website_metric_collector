#! python3
# -*- coding: utf-8 -*-


import datetime
# -----------------------------------------------------------------------------
#   File    :   utils;py.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------
import json
import uuid
import sys
import logging



from confluent_kafka import Producer


logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)


def print_message(message, level='ERROR'):
    if level == 'SUCCESS':
        logger.info(message)
    elif level == 'ERROR':
        logger.error(message)
    else:
        logger.debug(message)


def urls_from_env(env_url_str):
    """Return list of url|pattern from full the unique string websites input
     env_url_str is a websites argument string  represented
     as url1|pattern1;url2|pattern2 and read from env variable
     """
    return env_url_str.strip().split(';')


def produce_metric(kafka_broker, ca_path, cert_path, key_path, topic, messages):
    """Produce metric message to kafka
    Connect to kafka broker with producer configuration
    For each RequestResult, transform it to a dict then into string
    Produce string message to the kafka topic
    """
    producer = Producer({
        "bootstrap.servers": kafka_broker,
        "security.protocol": "ssl",
        "ssl.ca.location": ca_path,
        "ssl.certificate.location": cert_path,
        "ssl.key.location": key_path
    })

    for message in messages:
        payload = {k: v for k, v in vars(message).items() if
                   k in ('url', 'status', 'desc', 'error', 'latency', 'page_content_ok')}

        payload['at'] = datetime.datetime.utcnow().strftime('%m-%d-%Y, %H:%M:%S')

        # each message will have an unique id, in order to insert it once
        payload['message_id'] = f'{uuid.uuid4()}'

        kafka_message = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        producer.produce(topic, kafka_message)

        print_message(f"Produce metrics for url  : {payload['url']} into kafka", level='SUCCESS')

    producer.flush()
