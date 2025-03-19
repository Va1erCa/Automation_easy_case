import pandas as pd
import numpy as np
import asyncio, logging
from datetime import datetime


from config_py import settings, dir_name
from logger import set_logger

logger: logging.Logger = set_logger(log_set=settings.logging_generating)
logger.debug('Loading module <daily_sales_generator>')
# logger: logging.Logger = set_logger(log_set=settings.logging_uploading)
logger.debug('Loading module <daily_sales_uploader>')



async def gen_sales_store(store_cash_registers: int, store_rank: int, store_opening_hours: list[int]) -> bool :
    ...


async def main() :
    logger.info('The generator of the day`s sales was started.')

    stores = settings.store_chain.stores
    goods = settings.store_chain.goods
    path = settings.sales_storing_path

    time_start = datetime.now()

    # try :
    #     async with asyncio.TaskGroup() as tg :
    #         tasks = []
    for cash, rank, hours in zip(stores.cash_registers, stores.ranks, stores.opening_hours) :
        print(cash, rank, hours)
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

    return True

    # await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())

