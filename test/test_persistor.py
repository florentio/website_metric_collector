#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   collector.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

import os
import sys
import unittest
import uuid

sys.path.append("/usr/src/app")

from metrics.model.metric_db import MetricDB
from metrics.persistor.persistor import metricdb, consume_metric
import metrics.utils.constants as cst


class Persistor(unittest.TestCase):
    """
    Test persistor

    ...

    Methods
    -------
    test_persist_metric()
        test consume_metric function
    test_read_metric_db()
        test if db is been writting in the db as expected
    """

    def setUp(self):

        self.kafka_broker = os.environ['KAFKA_BOOTSTRAP_SERVER']
        self.topic = os.environ['KAFKA_TOPIC']

        # url to be used for database checking test
        self.url = 'https://centos.rip/fake'
        self.url_metric = (404, 'Not Found', True)

        self.metric_db = MetricDB(logging_name="MetricTestDB", db_uri=os.environ['METRIC_DB_URL'])

        # query to perform to check if data existed as expected
        self.query_metric = """
                                SELECT url, httpstatus, httpmessage, latency, result
                                FROM website,
                                    metric_latency,
                                    metric_status,
                                    metric_content_matcher
                                WHERE metric_status.website_id = website.id
                                AND metric_latency.website_id = website.id
                                AND metric_content_matcher.website_id = website.id
                                AND website.url = '{}';
                                """

    def test_persist_metric(self):
        consume_metric(self.kafka_broker, cst.KAFKA_SSL_CA_FILE, cst.KAFKA_SSL_CERT_FILE, cst.KAFKA_SSL_KEY_FILE,
                       self.topic, group_id=str(uuid.uuid4()), test=True)
        self.assertTrue(True, 'comsumer')

    def test_read_metric_db(self):
        db_connection = self.metric_db.has_connection()
        # test if connection is db is ok
        self.assertTrue(db_connection, 'DB Connection')
        if db_connection:
            response = metricdb.query_real_dict(self.query_metric.format(self.url))
            if response and response.tup:
                # test if website data has been inserted into each table  properly by the kafka consumer
                self.assertEqual(response.tup[0]['httpstatus'], self.url_metric[0], "Status metric Reader")
                self.assertEqual(response.tup[0]['httpmessage'], self.url_metric[1], "WebSite Reader")
                self.assertLess(float(response.tup[0]['latency']), cst.REQUEST_TIMEOUT, "Latency metric Reader")
                self.assertEqual(response.tup[0]['result'], self.url_metric[2], "Content pattern metric Reader")

            else:
                self.assertFalse(False, "Database data checking")


if __name__ == '__main__':
    unittest.main()
