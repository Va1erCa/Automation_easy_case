import pandas as pd
import numpy as np
import random
import asyncio, logging
from datetime import datetime, timedelta


from config_py import settings, StoreChainSettings, dir_name
from logger import set_logger
from chain_stores import ChainStores

# logger: logging.Logger = set_logger(log_set=settings.logging_generating)
# logger.debug('Loading module <daily_sales_generator>')
# # logger: logging.Logger = set_logger(log_set=settings.logging_uploading)
# logger.debug('Loading module <daily_sales_uploader>')

random.seed(42)
np.random.seed(42)


async def gen_sales_store(store_cash_registers: int, store_rank: int, store_opening_hours: list[int]) -> bool :
    ...


async def main() :
    logger: logging.Logger = await set_logger(log_set=settings.logging_generating)
    logger.info('The generator of the day`s sales was started.')

    time_start = datetime.now()
    operating_date = time_start - timedelta(days=1)

    logger.info(f'Operating date: {operating_date.date()}')

    # Checking for a day off
    if operating_date.weekday() == 6 :
        logger.info(f'It\'s a day off, so there\'s no sales data.')
        return

    # Basic operations
    await asyncio.sleep(0.01)
    chain_stores = ChainStores(chain_settings=settings.store_chain, processing_day=operating_date)
    await chain_stores.create_day()
    chain_stores.save_day()

    # stores = settings.store_chain.stores
    # goods = settings.store_chain.goods
    # path = settings.sales_storing_path

    # try :
    #     async with asyncio.TaskGroup() as tg :
    #         tasks = []
    # for cash, rank, hours in zip(stores.cash_registers, stores.ranks, stores.opening_hours) :
    #     print(cash, rank, hours)
                # tasks.append(
                #     tg.create_task(
                #         gen_sales_store(
                #             store_cash_registers: int, store_rank: int, store_opening_hours: list[int]
                #     client=client,
                #     selected_channels=settings.analyst.channel_selection_filter)

    #     tg_channels = task1.result()
    #     db_channels = task2.result()
    #
    #
    # except Exception as e :
    #     logger.error(f'Error: {e}')
    #     return False

    logger.info(f'The generator of the day`s sales was completed, '
                f'execution time - {(datetime.now() - time_start).total_seconds():.2f} seconds.')


    # await asyncio.sleep(0.1)
    return


if __name__ == '__main__':
    asyncio.run(main())

