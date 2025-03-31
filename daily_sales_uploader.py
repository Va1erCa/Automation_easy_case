# A module for regularly uploading the history of our store chain to the postgresql database.

import asyncio
from datetime import datetime
import pandas as pd
import re
from pathlib import Path, PurePath

from config_py import settings, dir_name
import logger as log
from logger import set_logger

log.logger = set_logger(log_common_set=settings.logging.common, log_specific_set=settings.logging.uploading)

from pgdb import Database, Rows, DBQueryResult
from exceptions import AppDBError
from app_types import DBReceipt, DBReceiptLine


async def receipts_upload(db: Database, df: pd.DataFrame) -> bool:
    try:
        # Getting a list of receipts and their time
        df_rc = df.groupby('doc_id')['receipt_time'].min().reset_index()

        # Cutting out the store/cashier's identification code from the receipt ID.
        df_rc['cr_receipt_code'] = df_rc['doc_id'].str[:2]

        # Reading the cash register directory from the postgres database
        res = db.read_rows(table_name='cash_register', columns_statement='id, store_id, cr_receipt_code')
        if not res.is_successful :
            raise AppDBError('Database operation error: couldn\'t read "cash registers" list.')

        # Creating a dict. with decoding <cr_receipt_code>: <key> - cr_receipt_code, <value> - store_id
        store_dict = {_[2] : _[1] for _ in res.value}
        df_rc['store_id'] = df_rc['cr_receipt_code'].map(store_dict)

        # Creating a dict. with decoding <cr_receipt_code>: <key> - cr_receipt_code, <value> - cash_register_id
        cash_reg_dict = {_[2] : _[0] for _ in res.value}
        df_rc['cash_reg_id'] = df_rc['cr_receipt_code'].map(cash_reg_dict)

        values: Rows = tuple(
            DBReceipt(
                id=rec['doc_id'],
                receipt_time=rec['receipt_time'],
                store_id=rec['store_id'],
                cash_reg_id=rec['cash_reg_id']
            )
            for rec in df_rc.to_dict(orient='records')
        )

        query = f"INSERT INTO receipt VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING "

        res = db.run_query(query=query, params=values, several=True)

        if res.is_successful :
            log.logger.info(f'The sales data have been successfully uploaded to the "receipt" table.')
        else :
            raise AppDBError(f'Database operation error: couldn\'t uploaded data to the table "receipt".')

    except Exception as e:
        log.logger.error(f'Error: {e}')
        return False

    return True


async def receipt_lines_upload(db: Database, df: pd.DataFrame) -> bool:
    try:
        df_rcl = df.copy()
        # Numbering the lines inside the receipts
        df_rcl['id_line'] = df_rcl.groupby(['doc_id']).cumcount() + 1

        # Reading the goods directory from the postgres database
        res = db.read_rows(table_name='goods', columns_statement='id, item_name')
        if not res.is_successful :
            raise AppDBError('Database operation error: couldn\'t read "goods" list.')

        # Getting the product ID by its name
        items_dict = {_[1] : _[0] for _ in res.value}
        df_rcl['id_item'] = df_rcl['item'].map(items_dict)

        values: Rows = tuple(
            DBReceiptLine(
                id=rec['id_line'],
                id_receipt=rec['doc_id'],
                id_item=rec['id_item'],
                amount=rec['amount']
            )
            for rec in df_rcl.to_dict(orient='records')
        )

        query = f"INSERT INTO receipt_line VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING "

        res = db.run_query(query=query, params=values, several=True)

        if res.is_successful :
            log.logger.info(f'The sales data have been successfully uploaded to the "receipt_line" table.')
        else :
            raise AppDBError(f'Database operation error: couldn\'t uploaded data to the table "receipt_line".')

    except Exception as e:
        log.logger.error(f'Error: {e}')
        return False

    return True


async def read_operation_day() -> pd.DataFrame:
    # df = pd.read_csv('./data/1_2.csv')

    df = pd.DataFrame()
    path = PurePath.joinpath(dir_name, settings.sales_storing_path)
    log.logger.debug(f'Reading data path: {path}')
    if Path(path).is_dir() :
        # Compiling "re"-pattern for the name of csv-sales data file
        regexp = re.compile(r'\d{1,4}_\d{1,4}.csv')
        # Finding all of csv files
        list_csv = []
        for el in Path(path).iterdir() :
            if regexp.match(el.name, 0) :
                list_csv.append(el)
        log.logger.debug(f'{len(list_csv)} data files were detected.')
        if len(list_csv) == 0 :
            log.logger.info(f'No download data files were found.')

        for el in list_csv :
            try :
                log.logger.debug(f'Reading data file: {el}.')
                df = pd.concat([df, pd.read_csv(el)])
            except Exception as e :
                log.logger.error(f'An error has occurred: {e}')

            # deleting processed file
            Path.unlink(PurePath.joinpath(path, el))

    return df


async def main() :
    log.logger.info('The uploader of the day`s sales was started.')
    time_start = datetime.now()

    db: Database = Database(settings.database_connection)
    if not db.is_connected :
        return False

    df_read_only = await read_operation_day()
    if len(df_read_only) == 0 :
        return False

    async with asyncio.TaskGroup() as tg :
        task1 = tg.create_task(receipts_upload(db=db, df=df_read_only))
        task2 = tg.create_task(receipt_lines_upload(db=db, df=df_read_only))

    if task1.result() and task2.result() :
        log.logger.info(f'The uploader of the day`s sales was completed, '
                        f'execution time - {(datetime.now() - time_start).total_seconds():.2f} seconds.')
    else :
        log.logger.error(f'Unfortunately, the process of uploading sales data to the database was not successful!')


if __name__ == '__main__':
    asyncio.run(main())

