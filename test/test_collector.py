#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   collector.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

import unittest
import os
import sys
sys.path.append("/usr/src/app")

from metrics.collector.collector import collect_metric_urls, produce_metric
from metrics.request.http_request import parse_url, HTTPRequests, RequestResult
import metrics.utils.constants as cst


class Collector(unittest.TestCase):
    """
    Test collector

    ...

    Methods
    -------
    test_parse_url()
        test parse_url function
    test_collect_metric_urls()
        test collect_metric_urls
    test_produce_metric()
       test produce_metric
    """

    def setUp(self):
        """
        Each element of urls is used for tes cases and follow this model:
        url|pattern : (expected http_status, expected http_message, pattern has found, url net location)
        """
        self.urls = {
            'https://centos.rip/fake|': (404, 'Not Found', True, 'centos.rip'),
            'http://localhost:8080|': (0, 'Could not resolve the url', False, 'localhost:8080'),
            'https://github.com|github': (200, 'OK', True, 'github.com'),
            'http://httpbin.org/|': (200, 'OK', True, 'httpbin.org'),
            'http://httpbin.org/status/200|': (200, 'OK', True, 'httpbin.org'),
            'http://httpbin.org/status/404|': (404, 'Not Found', True, 'httpbin.org'),
            'http://httpbin.org/status/502|': (502, 'Bad Gateway', True, 'httpbin.org'),
        }
        self.kafka_broker = os.environ['KAFKA_BOOTSTRAP_SERVER']
        self.topic = os.environ['KAFKA_TOPIC']
        self.responses = list()

    def test_parse_url(self):
        """
        Test if parse_url function parse url as excepted
        """
        for url, result in self.urls.items():
            loc = parse_url(url.split('|')[0]).netloc
            self.assertEqual(loc, result[3])

    def test_collect_metric_urls(self):
        """
        Test if collect_metric_urls collected metric as expected
        """
        responses = collect_metric_urls(HTTPRequests(urls=self.urls.keys(), timeout=cst.REQUEST_TIMEOUT))
        for response in responses:
            # test the status code and http message equality
            self.assertEqual(response.status, self.urls[response.url + "|" + response.content_pattern][0], response.url)
            # test if regex has been found or not as expected
            self.assertEqual(response.page_content_ok,
                             self.urls[response.url + "|" + response.content_pattern][2], response.url)
            # test if the latency is less than defined timeout which will assume
            # that the http response has been received in time
            self.assertLess(float(response.latency), cst.REQUEST_TIMEOUT, response.url)

    def test_produce_metric(self):
        """
        Test if produce_metric produc metric into kafka as expected
        """
        self.responses.append(RequestResult(url='https://github.com|github',
                                            status=200, desc='OK', content_pattern='github',
                                            latency='0.45', page_content_ok=True))
        self.responses.append(RequestResult(url='https://centos.rip/fake|', status=404,
                                            desc='NOT Found', content_pattern='alive',
                                            latency='0.34', page_content_ok=False))

        produce_metric(self.kafka_broker, cst.KAFKA_SSL_CA_FILE, cst.KAFKA_SSL_CERT_FILE,
                       cst.KAFKA_SSL_KEY_FILE, self.topic, self.responses)
        self.assertTrue(True, 'producer')


if __name__ == '__main__':
    unittest.main()
