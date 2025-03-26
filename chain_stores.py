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

# The data structure for storing the receipt
@dataclass(slots=True, frozen=True)
class Receipt :
    time_receipt: datetime
    receipt_lines: np.ndarray


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
        # Setting the seed-coefficient for the repeatability of the goods parameters
        np.random.seed(0)

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

        # Formation of the distribution of quantities for general use
        self.quantities: np.ndarray = np.floor(np.random.exponential(2, size=GOODS_CAPACITY*10) + 1).astype(int)


    def get_basket(self, items_in_basket: int) -> np.ndarray :
        return np.asarray(
            [
                ReceiptLine(i, a) for i, a in zip(np.random.choice(a=self.goods, size=items_in_basket),
                                                  np.random.choice(a=self.quantities, size=items_in_basket))
            ], dtype=ReceiptLine
        )


goods = Goods()


class CashRegister :

    def __init__(self, id_store: int, id_cash_reg: int, times: np.ndarray) :
        self._id_store: int = id_store
        self._id_cash_reg: int = id_cash_reg            # ascii_lowercase[id_cash_reg]
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
            [
                Receipt(
                    time_receipt=datetime.fromtimestamp(tms),
                    receipt_lines=goods.get_basket(lns)
                ) for tms, lns in zip(self._receipts_times, lines_in_receipts)
            ]
        )


    async def get_chunk(self, receipt: Receipt) -> pd.DataFrame:
        df = pd.DataFrame(
            [
                {
                    'id_store':self._id_store,
                    'id_cash_reg':self._id_cash_reg,
                    'doc_id': (
                        ascii_uppercase[self._id_store-1]+
                        ascii_lowercase[self._id_cash_reg-1]+
                        r.time_receipt.strftime('%Y%m%d%H%M%S')
                    ),
                    'time' : r.time_receipt,
                    'category_key' : ln.item.category_key,
                    'item_key' : ln.item.item_key,
                    'price' : ln.item.price,
                    'discount' : ln.item.discount,
                    'amount' : ln.amount
                }
                for r in [receipt] for ln in r.receipt_lines
            ]
        )

        return df


    async def save_cash_reg_day(self) -> pd.DataFrame :
        # Async run processes of creating sales for each store
        async with asyncio.TaskGroup() as tg :
            tasks = []
            for r in self._receipts :
                tasks.append(tg.create_task(self.get_chunk(receipt=r)))

        return pd.concat([task.result() for task in tasks])


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
        self._id_store = id_store   # ascii_uppercase[id_store]
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
                    id_cash_reg=i+1,
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


    async def save_store_day(self) -> pd.DataFrame:
        # Async run processes of saving sales for each cash register


        async with asyncio.TaskGroup() as tg :
            tasks = []
            for cr in self._cash_regs :
                tasks.append(tg.create_task(cr.save_cash_reg_day()))

        # for task in tasks :
        #     task.result()


        return pd.concat([task.result() for task in tasks])



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
                    id_store=i+1,
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


    async def save_day(self) :

        _check_path(path_save=settings.sales_storing_path)

        async with asyncio.TaskGroup() as tg :
            tasks = []
            for s in self._stores :
                tasks.append(tg.create_task(s.save_store_day()))

        # Async run tasks of saving sales for each store in a data frame
        df = pd.concat([task.result() for task in tasks])

        # Subsequent processing of the data frame
        _save_to_csv(df=df, path_save=settings.sales_storing_path, name='temp.csv')

        return df

from pathlib import Path, PurePath


def _check_path(path_save: str) :
    path = PurePath.joinpath(dir_name, path_save)
    if not Path(path).is_dir() :
        # Creating a log folder if it doesn't exist yet
        Path.mkdir(path)


def _save_to_csv(df: pd.DataFrame, path_save: str, name: str) -> bool :
    path = PurePath.joinpath(dir_name, path_save)
    df.to_csv(PurePath.joinpath(path, name), index=False)

    return True




if __name__ == '__main__' :
    ...
