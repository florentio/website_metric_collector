#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   constants.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

KAFKA_SSL_CA_FILE = '/usr/src/app/certs/ca.pem'
KAFKA_SSL_KEY_FILE = '/usr/src/app/certs/service.key'
KAFKA_SSL_CERT_FILE = '/usr/src/app/certs/service.cert'
METRIC_COLLECTOR_FREQ = 5
REQUEST_TIMEOUT = 5
HTTP_STATUS_CODES = (204, 301, 302, 303, 307, 308)
