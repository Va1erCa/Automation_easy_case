# A module for the regular formation of the history of our network of stores

import pandas as pd
import numpy as np
import random
import asyncio, logging
from datetime import datetime, timedelta

from config_py import settings, StoreChainSettings, dir_name
import logger as log
from logger import set_logger #, logger

from chain_stores import ChainStores

log.logger = set_logger(log_set=settings.logging_generating)


# logger = logger.logger
# logger: logging.Logger = set_logger(log_set=settings.logging_generating)
# logger.debug('Loading module <daily_sales_generator>')
# # logger: logging.Logger = set_logger(log_set=settings.logging_uploading)
# logger.debug('Loading module <daily_sales_uploader>')


async def main() :
    # await set_logger(log_set=settings.logging_generating)
    log.logger.info('The generator of the day`s sales was started.')

    time_start = datetime.now()
    operating_date = time_start - timedelta(days=1)

    log.logger.info(f'Operating date: {operating_date.date()}')

    # Checking for a day off
    if operating_date.weekday() == 6 :
        log.logger.info(f'It\'s a day off, so there\'s no sales data.')
        return

    # Basic operations
    # await asyncio.sleep(0.01)
    chain_stores = ChainStores(chain_settings=settings.store_chain, processing_day=operating_date)
    await chain_stores.create_day()
    await chain_stores.save_day()

    # pass

    # try :
    #
    # except Exception as e :
    #     logger.error(f'Error: {e}')
    #     return False

    log.logger.info(f'The generator of the day`s sales was completed, '
                f'execution time - {(datetime.now() - time_start).total_seconds():.2f} seconds.')

    # await asyncio.sleep(0.1)
    return


if __name__ == '__main__':
    asyncio.run(main())

