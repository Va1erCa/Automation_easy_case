import pandas as pd
import numpy as np
import random
import asyncio
from datetime import datetime
from string import ascii_uppercase, ascii_lowercase

from config_py import settings, StoreChainSettings, dir_name
import logger as log

# logger: logging.Logger = set_logger(log_set=settings.logging_generating)
# logger.debug('Loading module <daily_sales_generator>')
# # logger: logging.Logger = set_logger(log_set=settings.logging_uploading)
# logger.debug('Loading module <daily_sales_uploader>')

# random.seed(42)
# np.random.seed(42)

class ReceiptLine :
    ...


class Receipt :
    ...


class CashRegister :

    def __init__(self, id_store: str, id_cash_reg: int, times: np.ndarray) :
        self._id_store: str = id_store
        self._id_cash_reg: str = ascii_lowercase[id_cash_reg]
        #
        self._receipts_times: np.ndarray = times
        #
        self._receipts: list[Receipt] = []
        log.logger.debug(f'The "{self._id_cash_reg}" cash register has been created in the "{self._id_store}" store '
                         f'({len(self._receipts_times)} sales will be processed).')

    async def create_cash_reg_day(self):
        # self._receipts_times =
        ...
        # times=np.random.choice(a=self._times, size=self._daily_load)



class Store :

    def __init__(self,
                 id_store: int,
                 num_cash_regs: int,
                 # rank: int,
                 opening_hour: int,
                 closing_hour: int,
                 processing_date: datetime,
                 store_daily_load: float) :
        #
        self._id_store = ascii_uppercase[id_store]
        self._num_cash_regs: int = num_cash_regs
        # self._rank: int = rank
        self._opening_hour: int  = opening_hour
        self._closing_hour: int = closing_hour
        self._processing_date: datetime = processing_date
        self._times: np.ndarray | None = None
        self._store_daily_load : float = store_daily_load
        self._cash_regs: list[CashRegister] = []
        #
        log.logger.debug(
            f'The store "{self._id_store}" has been created with params: number of cash registers: {self._num_cash_regs} / '
            f'opening hours: from {self._opening_hour} to {self._closing_hour} / daily load: {self._store_daily_load}')


    async def create_store_day(self) :
        clear_hour = dict(minute=0, second=0, microsecond=0)
        ts_start = self._processing_date.replace(hour=self._opening_hour, **clear_hour).timestamp()
        ts_stop = self._processing_date.replace(hour=self._closing_hour, **clear_hour).timestamp()

        self._times = np.arange(start=ts_start, stop=ts_stop, step=settings.store_chain.min_sec_per_cash_transaction)
        daily_load = len(self._times) * self._store_daily_load

        # Creating all cash_registers for store
        for i in range(self._num_cash_regs) :
            self._cash_regs.append(
                CashRegister(
                    id_store=self._id_store,
                    id_cash_reg=i,
                    times=np.random.choice(
                        a=self._times,
                        size=round(daily_load * random.uniform(*settings.store_chain.range_of_cash_regs_daily_load))
                    )
                )
            )

        # Async run processes of creating sales for each store
        async with asyncio.TaskGroup() as tg :
            tasks = []
            for cr in self._cash_regs :
                tasks.append(tg.create_task(cr.create_cash_reg_day()))

        for task in tasks :
            task.result()


class ChainStores :

    def __init__(self, chain_settings: StoreChainSettings, processing_day: datetime) :

        seed_factor = int(processing_day.strftime('%Y%m%d'))
        random.seed(seed_factor)
        np.random.seed(seed_factor)

        self._chain_settings = chain_settings
        self._processing_day = processing_day
        self._chain_daily_load = random.uniform(*settings.store_chain.range_of_chain_daily_load)
        self._stores: list[Store] = []

        log.logger.debug(f'The store chain will be created with the following parameters: seed factor: {seed_factor} /'
                         f'stores: {len(self._chain_settings.stores.cash_registers)} / '
                         f'daily load: {self._chain_daily_load} processing day: {self._processing_day.date()}.')


    async def create_day(self) :
        # Creating all stores
        for i in range(len(self._chain_settings.stores.cash_registers)) :
            self._stores.append(
                Store(
                    id_store=i,
                    num_cash_regs=self._chain_settings.stores.cash_registers[i],
                    opening_hour=self._chain_settings.stores.opening_hours[i][0],
                    closing_hour=self._chain_settings.stores.opening_hours[i][1],
                    processing_date=self._processing_day,
                    store_daily_load=self._chain_daily_load * self._chain_settings.stores.ranks[i] / 100.0
                )
            )

        # Creating tasks for async run processes of creating sales for each store
        async with asyncio.TaskGroup() as tg :
            tasks = []
            for s in self._stores :
                tasks.append(tg.create_task(s.create_store_day()))

        # Async run tasks of creating sales for each store
        for task in tasks :
            task.result()

    def save_day(self) :
        ...



if __name__ == '__main__' :
    ...
