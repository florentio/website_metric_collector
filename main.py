#!/usr/bin/env python3
# Copyright (c) 2018 Aiven, Helsinki, Finland. https://aiven.io/

# this file has been edited by Florentio accordingly to the usecase

import argparse
import os

from metrics.collector.collector import collect_metrics
from metrics.persistor.persistor import consume_metric
from metrics.utils.helpers import print_message
import metrics.utils.constants as cst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collector', action='store_true', default=False, help="Run metric collector")
    parser.add_argument('--persistor', action='store_true', default=False, help="Run metric persistor")
    args = parser.parse_args()
    args.kafka_broker = os.environ.get('KAFKA_BOOTSTRAP_SERVER', None)
    args.ca_path = cst.KAFKA_SSL_CA_FILE
    args.key_path = cst.KAFKA_SSL_KEY_FILE
    args.cert_path = cst.KAFKA_SSL_CERT_FILE
    args.topic = os.environ.get('KAFKA_TOPIC', None)

    if not validate_args(args):
        exit(1)

    kwargs = {k: v for k, v in vars(args).items() if k not in ("collector", "persistor")}
    if args.collector:
        collect_metrics(**kwargs)
    elif args.persistor:
        consume_metric(**kwargs)


def validate_args(args):
    if not args.kafka_broker or not args.topic:
        print_message("kafka broker uri and kafka topic must be provided")
        return False

    for path_option in ("ca_path", "key_path", "cert_path"):
        path = getattr(args, path_option)
        if not os.path.isfile(path):
            print_message(f"Failed to open --{path_option.replace('_', '-')} at path: {path}.\n"
                          f"You can retrieve these details from Overview tab in the Aiven Console")
            return False
    if args.collector and args.persistor:
        print_message("--collector and --persistor are mutually exclusive")
        return False
    elif not args.collector and not args.persistor:
        print_message("--collector or --persistor are required")
        return False

    return True


if __name__ == '__main__':
    main()
