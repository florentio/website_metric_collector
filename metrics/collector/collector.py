#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   collector.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------
import os
import time
from multiprocessing import Process

import metrics.utils.constants as cst
from metrics.request.http_request import HTTPRequests, http_response
from metrics.utils.helpers import urls_from_env, produce_metric, print_message


def collect_metric_urls(requests: HTTPRequests):
    """
    Loops through the list of URLs and performs the checks.
    :param requests:
    :type requests: NamedTuple
    :return: list
    """

    responses = list()
    for url in requests.urls:
        # since each website url is in the format <url>|<content pattern>, we must split to read each part
        try:
            my_url, content_pattern = url.strip().split('|')
        except:
            print_message(f'Failed to read url from the given text {url}, missing | delimiter ')
            continue

        print_message(f'Start collecting metrics for url  : {my_url} ', level='DEBUG')
        responses.append(http_response(my_url, requests.timeout, content_pattern))
        print_message(f'End collecting metrics for url  : {my_url} ', level='DEBUG')
    return responses


def run(kafka_config, website_urls):
    """
    Collect metric and produce to kafka
    :param kafka_config: kafka configuration for producer
    :type kafka_config: dict
    :param website_urls: urls and regex
    :type website_urls: str
    :return:
    """

    _kafka_broker = kafka_config['kafka_broker']
    _ca_path = kafka_config.get('ca_path', cst.KAFKA_SSL_CA_FILE)
    _cert_path = kafka_config.get('cert_path', cst.KAFKA_SSL_CERT_FILE)
    _key_path = kafka_config.get('key_path', cst.KAFKA_SSL_KEY_FILE)
    _topic = kafka_config['topic']

    responses = collect_metric_urls(HTTPRequests(urls=website_urls, timeout=cst.REQUEST_TIMEOUT))

    # produce response to kafka
    produce_metric(_kafka_broker, _ca_path, _cert_path, _key_path, _topic, responses)


def collect_metrics(**kafka_config):
    """
    Collect metric process entrypoint
    :param kafka_config: kafka configs
    :type kafka_config: dict
    :return:
    """

    freq = int(os.environ.get('METRIC_COLLECTOR_FREQ', cst.METRIC_COLLECTOR_FREQ))

    # read urls from env variable else use sample value in constants
    website_urls = urls_from_env(os.environ['WEBSITES'])

    try:
        while True:
            print_message('Collector launched', level='DEBUG')
            p = Process(target=run, args=(kafka_config, website_urls))
            p.start()
            p.join()

            # wait freq second between each metric collections
            time.sleep(freq)

    except KeyboardInterrupt:
        print_message('Collector exited.')
