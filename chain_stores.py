import pandas as pd
import numpy as np
import random
import asyncio
from datetime import datetime
from string import ascii_uppercase, ascii_lowercase

from config_py import settings, StoreChainSettings, dir_name


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

    def __init__(self, id_store: str, id_cash_reg: int, times: np.ndarray ) :
        self._id_store: str = id_store
        self._id_cash_reg: str = ascii_lowercase[id_cash_reg]
        self._receipts_times: np.ndarray = times
        self._receipts = []


    async def create_cash_reg_day(self):
        # self._receipts_times =
        ...

        print(f'In store {self._id_store} cash_register created.')


class Store :

    def __init__(self,
                 id_store: int,
                 num_cash_regs: int,
                 rank: int,
                 opening_hour: int,
                 closing_hour: int,
                 processing_date: datetime) :
        #
        self._id_store = ascii_uppercase[id_store]
        self._num_cash_regs: int = num_cash_regs
        self._rank: int = rank
        self._opening_hour: int  = opening_hour
        self._closing_hour: int = closing_hour
        self._processing_date: datetime = processing_date
        self._times: np.ndarray | None = None
        self._daily_load : int = 0
        self._cash_regs: list[CashRegister] = []


    async def create_store_day(self) :
        #
        print(self._id_store, self._num_cash_regs, self._rank, self._opening_hour, self._closing_hour)
        clear_hour = dict(minute=0, second=0, microsecond=0)
        ts_start = self._processing_date.replace(hour=self._opening_hour, **clear_hour).timestamp()
        ts_stop = self._processing_date.replace(hour=self._closing_hour, **clear_hour).timestamp()

        self._times = np.arange(start=ts_start, stop=ts_stop, step=settings.store_chain.min_sec_per_cash_transaction)
        self._daily_load = round(len(self._times) * random.uniform(*settings.store_chain.range_of_chain_daily_load))

        # Creating all cash_registers for store
        for i in range(self._num_cash_regs) :
            self._cash_regs.append(
                CashRegister(
                    id_store=self._id_store,
                    id_cash_reg=i,
                    times=np.random.choice(a=self._times, size=self._daily_load)
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
        self._chain_settings = chain_settings
        self._processing_day = processing_day
        self._stores: list[Store] = []

    async def create_day(self) :
        # Creating all stores
        for i in range(len(self._chain_settings.stores.cash_registers)) :
            self._stores.append(
                Store(
                    id_store=i,
                    num_cash_regs=self._chain_settings.stores.cash_registers[i],
                    rank=self._chain_settings.stores.ranks[i],
                    opening_hour=self._chain_settings.stores.opening_hours[i][0],
                    closing_hour=self._chain_settings.stores.opening_hours[i][1],
                    processing_date=self._processing_day
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
