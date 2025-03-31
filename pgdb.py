# A class for working with a database
#
#   Class name: Database
#   Methods:
#       run_query(table_name, params, several) - main method
#       read_rows(table_name, columns_statement, condition_statement, order_by_statement, limit)
#       search_table(table_name)
#       create_table(table_name, columns_statement, overwrite)
#       insert_rows(table_name, values)
#       update_data(table_name, set_statement, condition_statement)
#       delete_rows(table_name, condition_statement)
#       count_rows(table_name)
#       close_connection()
#
# >>>  Usage examples in the <pgdb_example.py> module
#

import psycopg2
from psycopg2 import extensions
from dataclasses import dataclass
from typing import NamedTuple

import logger as log
from config_py import DBConnectionSettings

# Type's hints
Row = NamedTuple
Rows = tuple[Row, ...]
ConnectionType = psycopg2.extensions.connection

# The data structure returned by most methods
@dataclass(slots=True, frozen=True)
class DBQueryResult :
    is_successful: bool    # this is the success flag
    value: tuple | int | None    # received data


class Database :
    #    # a class for working with the database connection (we use singleton pattern)
    # __db_instance = None
    #
    # def __new__(cls, *args, **kwargs) :
    #     if not cls.__db_instance :
    #         cls.__db_instance = super().__new__(cls)
    #     return cls.__db_instance

    def __init__(self, db_connect_set: DBConnectionSettings)  -> object:
        ''' Constructor '''
        self.db_connect_set = db_connect_set
        try :
            self.connect: ConnectionType = psycopg2.connect(
                **db_connect_set.model_dump()
            )
            log.logger.debug('The database has been successfully connected.')
            self.is_connected = True

        except Exception as e :
            log.logger.error(f'An error occurred while connecting database: {e}')
            self.is_connected = False

    def __del__(self) :
        self.close_connection()


    def run_query(self, query: str, params: tuple = (), several: bool = False) -> DBQueryResult :
        ''' Main method '''
        try :
            with self.connect:
                with self.connect.cursor() as cursor :
                    if several :
                        cursor.executemany(query, params)
                    else :
                        cursor.execute(query, params)

                    # We return the data if the request suggested it
                    if cursor.description :
                        return DBQueryResult(True, cursor.fetchall())

                    # In other cases, we return the number of affected rows
                    return DBQueryResult(True, cursor.rowcount)

        except Exception as e :
            log.logger.error(f"An error occurred while executing the request: {e}")
            return DBQueryResult(False, None)


    def search_rows(self, table_name: str, search_column: str = 'id', search_value = 0) -> bool :
        ''' A simple searcher for one column '''
        if table_name :
            query = f'SELECT count(*) FROM {table_name} WHERE {search_column} = {search_value}'
            res = self.run_query(query)
            if res.is_successful and res.value[0][0] > 0 :
                return True
        return False


    def read_rows(self,
                  table_name: str,
                  columns_statement: str = '*',
                  condition_statement='',
                  order_by_statement='',
                  limit: int = 0) -> DBQueryResult :
        ''' A simple line reader '''
        if table_name :
            query = f'SELECT {columns_statement} FROM {table_name}'
            if condition_statement :
                query += f' WHERE {condition_statement}'
            if order_by_statement :
                query += f' ORDER BY {order_by_statement}'
            if limit > 0 :
                query += f' LIMIT {limit}'
            return self.run_query(query)
        return DBQueryResult(False, None)


    def search_table(self, table_name: str) -> bool :
        ''' Table search '''
        if table_name :
            query = (f'SELECT table_name FROM information_schema.tables '
                    f'WHERE table_schema=\'public\' AND table_type=\'BASE TABLE\' '
                    f'AND table_name = \'{table_name}\'')
            res = self.run_query(query)
            if res.is_successful and len(res.value) != 0 :
                return True
        return False


    def create_table(self,
                     table_name: str,
                     columns_statement: str,
                     overwrite: bool = False) -> DBQueryResult :
        ''' Creating a new table '''
        if table_name and columns_statement :
            if self.search_table(table_name) :
                if overwrite :
                    query = f'DROP TABLE {table_name} CASCADE'
                    if not self.run_query(query).is_successful :
                        log.logger.debug(f'The already existing table "{table_name}" has not been deleted.')
                        return DBQueryResult(False, None)
                    log.logger.debug(f'The already existing table "{table_name}" has been deleted.')
                else:
                    log.logger.debug(f'Error, table "{table_name}" is already there.')
                    return DBQueryResult(False, None)
            query = f'CREATE TABLE {table_name} ({columns_statement})'
            return self.run_query(query)
        else :
            return DBQueryResult(False, None)


    def insert_rows(
            self,
            table_name: str,
            values: Rows,
            insert_fields: tuple[str] | None=None,
            returning_field: str | None=None
    ) -> DBQueryResult:
        ''' Inserting one or multiple rows into a table. '''
        if table_name and len(values) > 0 and len(values[0]) > 0 :
            fields_str = ''
            if insert_fields is not None:
                fields_str += f'({', '.join(insert_fields)})'
            placeholders = ', '.join(['%s'] * len(values[0]))
            query = f"INSERT INTO {table_name} {fields_str} VALUES ({placeholders})"
            if returning_field is not None:
                query += f" RETURNING {returning_field}"
            if len(values)>1:
                several = True
            else:
                # if insert single row
                several = False
                values = values[0]

            return self.run_query(query, params=values, several=several)
        return DBQueryResult(False, 0)


    def update_data(self,
                    table_name: str,
                    set_statement: str,
                    condition_statement: str) -> DBQueryResult :
        ''' Updating the data in the table. '''
        if table_name and set_statement and condition_statement :
            query = (f'UPDATE {table_name} SET {set_statement} '
                     f'WHERE {condition_statement}')
            return self.run_query(query)
        return DBQueryResult(False, None)


    def delete_rows(self,
                    table_name: str,
                    condition_statement: str = '')  -> DBQueryResult :
        ''' Deleting rows from a table. '''
        if table_name :
            query = (f'DELETE FROM {table_name}')
            if condition_statement :
                query += f' WHERE {condition_statement}'
            return self.run_query(query)
        return DBQueryResult(False, None)


    def count_rows(self, table_name):
        '''Getting the number of rows in a table.'''
        if table_name :
            query = f'SELECT COUNT(*) FROM {table_name}'
            res = self.run_query(query).value[0][0]
            return DBQueryResult(True, res)
        return DBQueryResult(False, None)


    def close_connection(self) :
        ''' Closing the database connection '''
        try :
            self.connect.close()
            log.logger.debug('The connection to the database is closed.')
        except Exception as e :
            log.logger.debug(f'An error occurred when closing the connection: {e}')
