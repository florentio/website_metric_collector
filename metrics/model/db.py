#! python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
#   File    :   db.py
#   Date	: 24 Jan 2021
#
#   Author: Florentio
# ----------------------------------------------------------

from metrics.utils.helpers import print_message


class QuerySet:
    """
    SQL Query response mapper class
    """

    def __init__(self, tup):
        self.tup = tup

    def __iter__(self):
        for row in self.tup:
            yield row

    def __len__(self):
        return len(self.tup)

    def __bool__(self):
        return hasattr(self.tup, '__getitem__') and len(self.tup) != 0

    def __jsonnull__(self):
        if self.__bool__():
            if self.tup[0]:
                return True
        return False

    def __getitem__(self, item):
        if hasattr(self.tup, '__getitem__'):
            return self.tup[item]
        return None


class DB:
    """
    SQL DataBase Class  for connecting, querying any SQL Database

    ...

    Attributes
    ----------
    logging_name : str
        The  database name for log
    db_uri : str
        The sql database URI
    _is_connected : boolean
        if connection is ok
    conn : object
        connection object

    Methods
    -------
    _connect()
        connection method to be override
    connect()
        db connection method
    has_connection()
        method to check connection or etablish it if not
    _close()
        close db method to be override
    close()
        db close method
    _query()
        query method to be override
    query()
        db query method
    __query_real_dict()
        db query with dict result fashion mode  method to be override
    query_real_dict()
        db query with dict result fashion mode
    """

    def __init__(self, logging_name, db_uri):
        """
        Parameters
        ----------
        logging_name : str
            The  database name for log
        db_uri : str
            The sql database URI
        """

        self.db_uri = db_uri
        self.name = logging_name
        self._is_connected = False
        self.conn = None

    def _connect(self):
        raise NotImplemented()

    def connect(self):
        """
        Etablish connection to the database
        """
        try:
            if self.conn is not None:
                self.close()
            self.conn = self._connect()
            if self.conn is not None:
                self._is_connected = True
            print_message(f'Database connexion {self.name} success.', level='SUCCESS')
        except Exception:
            self.close()
        finally:
            return self._is_connected

    def has_connection(self):
        """
        Etablish connection to the database if there is no existing connection
        Check is the connection is alive by making a simple SQL query test
        """

        try:
            if not self._is_connected:
                self.connect()
            if self._is_connected:
                q = self.query('SELECT 1')
                self._is_connected = q.__bool__
        except Exception:
            self.close()
        finally:
            return self._is_connected

    def _close(self):
        raise NotImplemented()

    def close(self):
        """
        Close the database connection
        """
        try:
            if self.conn is not None:
                self._close()
                print_message(f'Database connexion {self.name} closed.')
        except Exception as e:
            print_message(f'Database connexion  {self.name} Failed to close {e}')
        finally:
            self.conn = None
            self._is_connected = False

    def _query(self, q, p):
        raise NotImplemented()

    def query(self, q, p=None):
        """
        Query the database with a sql query and return the result as row/column model
        :param q: the sql query
        :type q: str
        :param p: the sql query params
        :return: QuerySet
        """

        if not self._is_connected or self.conn is None:
            if not self.connect():
                return None
        try:
            return QuerySet(self._query(q, p))
        except Exception as e:
            self.close()
            print_message(f'Database connexion {self.name} query failed for {q} {p} with {e}')
            return None

    def _query_real_dict(self, q, p):
        raise NotImplemented()

    def query_real_dict(self, q, p=None):
        """
        Query the database with a sql query and return the result as list of dict
        :param q: the sql query
        :type q: str
        :param p: the sql query params
        :return: QuerySet
        """

        if not self._is_connected or self.conn is None:
            # try to reconnect
            if not self.connect():
                return None
        try:
            return QuerySet(self._query_real_dict(q, p))
        except Exception as e:
            self.close()
            print_message(f'Database connexion {self.name} query failed for {q} {p} with {e}')
            return None
