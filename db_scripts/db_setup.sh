#!/usr/bin/sh

echo $METRIC_DB_URL

echo 'Prepare DB'
psql $METRIC_DB_URL -f /home/script/schemas.sql
psql $METRIC_DB_URL -f /home/script/functions.sql

echo 'DB up'

