#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   persistor.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------


import os

from confluent_kafka import Consumer

from metrics.model.metric_db import MetricDB
from metrics.utils.helpers import print_message

# metricdb instanciation
metricdb = MetricDB(logging_name="MetricDB", db_uri=os.environ.get('METRIC_DB_URL', None))


def consume_metric(kafka_broker, ca_path, cert_path, key_path, topic, group_id='default', test=False, persist=True):
    """

    :param kafka_broker: kafka service uri (<host>:<port>)
    :type kafka_broker:str
    :param ca_path: ca.pem path
    :type ca_path:str
    :param cert_path: service.cert path
    :type cert_path:str
    :param key_path: service.key path
    :type key_path:str
    :param topic: kafka topic
    :type topic:str
    :param group_id: the consumer group
    :type group_id:str
    :param test: if it's for test case
    :type test:bool
    :param persist: persist message into database
    :type persist:bool
    :return:
    """

    # consumer configuration
    conf = {
        "enable.auto.commit": True,
        'group.id': group_id,
        'session.timeout.ms': 6000,
        "bootstrap.servers": kafka_broker,
        "security.protocol": "ssl",
        "ssl.ca.location": ca_path,
        "ssl.certificate.location": cert_path,
        "ssl.key.location": key_path,
        "auto.offset.reset": "earliest"
    }

    # Create Consumer instance
    c = Consumer(conf)

    def print_assignment(consumer, partitions):
        print_message(f'Consumer: {consumer}, Assignment:{partitions}', level='DEBUG')

    # Subscribe to topics
    c.subscribe([topic], on_assign=print_assignment)
    running = True
    try:
        while running:
            msg = c.poll(timeout=1.0)
            if not msg:
                continue
            if msg.error():
                print_message(f'Consumer error: {msg.error()}')
                continue

            if test:
                running = False

            # Proper message
            print_message(f'{msg.topic()} [{msg.partition()}] '
                          f'at offset {msg.offset()} with key {msg.key()}', level='DEBUG')
            data = msg.value().decode('utf-8')
            print_message(f'Received message: {data}', level='DEBUG')
            if persist:
                persist_metric(data)

    except KeyboardInterrupt:
        print_message('Consumer exited')

    finally:
        # Close down consumer to commit final offsets.
        c.close()


def persist_metric(metric_data):
    """
    Save message into the database
    :param metric_data: dict
    :return:
    """

    if not metricdb.has_connection():
        print_message('No available connection to metric database')
        return

    response = metricdb.query_real_dict("select public.add_metric_data('{}')".format(metric_data))
    if response and response.tup:
        print_message(f"Message {response.tup[0]['add_metric_data']} saved successfully", level='SUCCESS')
