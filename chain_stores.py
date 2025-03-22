import pandas as pd
import numpy as np
import random
import asyncio
from datetime import datetime
from dataclasses import dataclass
from string import ascii_uppercase, ascii_lowercase

from config_py import settings, StoreChainSettings, dir_name
import logger as log

# logger: logging.Logger = set_logger(log_set=settings.logging_generating)
# logger.debug('Loading module <daily_sales_generator>')
# # logger: logging.Logger = set_logger(log_set=settings.logging_uploading)
# logger.debug('Loading module <daily_sales_uploader>')

# random.seed(42)
# np.random.seed(42)

RANGE_CATEGORIES = (0, len(settings.store_chain.goods.categories))

# The total number of all products of all categories
GOODS_CAPACITY = sum(settings.store_chain.goods.category_capacity) + RANGE_CATEGORIES[1]


# The data structure for storing the "skeleton" of the product
@dataclass(slots=True, frozen=True)
class Item :
    category_key: int
    item_key: int
    price: int
    discount: float

# The data structure for storing the receipt line
@dataclass(slots=True, frozen=True)
class ReceiptLine :
    item: Item
    amount: int

#
# class Item :
#     def __init__(self, category_key: int, item_key: int, price: int, discount: int) :
#         self._category_key: int = category_key
#         self._item_key: int = item_key
#         self._price: int = price
#         self._discount: int = discount

def get_prices(sample_size: int) :
    min_p, max_p = settings.store_chain.goods.price_distribution.range_prices
    mean_p = settings.store_chain.goods.price_distribution.mean_price

    # Generating a lognormal distribution
    data = np.random.lognormal(
        mean=np.log(mean_p),
        sigma=(1.38-0.6*(mean_p/max_p/0.05)),   # the empirical formula
        size=GOODS_CAPACITY*10
    ).round(-1)

    # Bringing it to the range from min price to max price in chain stores
    data = np.clip(a=(data - data.min() + 10), a_min=min_p, a_max=max_p)

    return np.random.choice(a=data, size=sample_size)


class Goods :

    def __init__(self) :
        # Formation of prices for goods
        prices = get_prices(sample_size=GOODS_CAPACITY)

        # Formation of discounts on goods
        discounts = np.random.choice(
            a=settings.store_chain.goods.discounts.discounts_values,
            p=settings.store_chain.goods.discounts.discounts_probs,
            size=GOODS_CAPACITY
        )
        t_goods = (
            [
                [x, y] for x in range(*RANGE_CATEGORIES)
                       for y in range(0, settings.store_chain.goods.category_capacity[x] + 1)
            ]
        )
        # Formation of goods
        self.goods: np.ndarray = np.array([Item(c, i, p, d) for (c, i), p, d in zip(t_goods, prices, discounts)])

        #
        self.quantities: np.ndarray = np.floor(np.random.exponential(2, size=GOODS_CAPACITY*10) + 1).astype(int)


    def get_basket(self, items_in_basket: int) -> np.ndarray :
        return np.asarray(
            [
                ReceiptLine(i, a) for i, a in zip(np.random.choice(a=self.goods, size=items_in_basket),
                                                  np.random.choice(a=self.quantities, size=items_in_basket))
            ]
        )


goods = Goods()

#
# def get_receipt_lines(amount: int) -> list[ReceiptLine]:
#     ...


class Receipt :

    def __init__(self, time_receipt: any, lines_in_receipt: int) :
        self._time_receipt = datetime.fromtimestamp(time_receipt)
        self._lines: np.ndarray = goods.get_basket(lines_in_receipt)


class CashRegister :

    def __init__(self, id_store: str, id_cash_reg: int, times: np.ndarray) :
        self._id_store: str = id_store
        self._id_cash_reg: str = ascii_lowercase[id_cash_reg]
        #
        self._receipts_times: np.ndarray = times
        #
        self._receipts: np.ndarray | None = None
        log.logger.debug(f'The "{self._id_cash_reg}" cash register has been created in the "{self._id_store}" store '
                         f'({len(self._receipts_times)} sales will be processed).')


    async def create_cash_reg_day(self) :
        # Sorting receipts by time
        self._receipts_times.sort()
        # Generating the number of lines in each receipt (from goods.quantities - exponential distribution)
        lines_in_receipts: np.ndarray[int] = np.random.choice(a=goods.quantities,size=len(self._receipts_times))
        # Creating all receipts
        self._receipts = np.asarray(
            [Receipt(tms, lns) for tms, lns in zip(self._receipts_times, lines_in_receipts)]
        )


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
