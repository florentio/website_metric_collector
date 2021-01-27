#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   db.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

import psycopg2
from psycopg2.extras import RealDictCursor

from metrics.model.db import DB


class MetricDB(DB):
    """
    Metric DB Class

    ...

    Attributes
    ----------
    logging_name : str
        The  database name for log
    db_uri : str
        The sql database URI

    Methods
    -------
    _connect()
        db connection method
    _close()
        db close method
    _query()
       db query method
    _query_real_dict()
       db query with dict result fashion mode

    """

    def __init__(self, logging_name, db_uri):
        """
        Constructor
        :param logging_name: the name of the connection
        :param db_uri: the postgresql db URI
        """
        super(MetricDB, self).__init__(logging_name=logging_name, db_uri=db_uri)

    def _connect(self):
        # Connect to postgresql database
        conn = psycopg2.connect(self.db_uri)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        return conn

    def _query(self, q, p):
        """
        Query the database
        :param q: the sql query
        :type q: str
        :param p: the sql query params
        :return: QuerySet
        """

        cur = self.conn.cursor()
        cur.execute(q, vars=p)
        if cur.rowcount > 0:
            try:
                ret = cur.fetchall()
                return ret
            except:
                return None
        else:
            return None

    def _query_real_dict(self, q, p):
        """
        Query the database with RealDictCursor cursor
        :param q: the sql query
        :type q: str
        :param p: the sql query params
        :return: QuerySet
        """
        cur = self.conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(q, vars=p)
        if cur.rowcount > 0:
            try:
                return cur.fetchall()
            except:
                return None
        else:
            return None

    def _close(self):
        # Close the db connection
        self.conn.close()
