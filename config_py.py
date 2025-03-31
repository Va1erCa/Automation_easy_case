# A module for processing application settings.

from pathlib import Path, PurePath
from pydantic import BaseModel, Field, PositiveInt, computed_field
import logging

logger_level = dict(NOTSET=logging.NOTSET,
                    DEBUG=logging.DEBUG,
                    INFO=logging.INFO,
                    WARNING=logging.WARNING,
                    ERROR=logging.ERROR,
                    CRITICAL=logging.CRITICAL)

class DBConnectionSettings(BaseModel) :
    host: str = Field(default='localhost', description='connection host')
    port: PositiveInt = Field(default=5432, description='connection port')
    dbname: str = Field(default='household_goods_chain', description='connection data base name')
    user: str = Field(default='postgres', description='connection user')
    password: str = Field(default='123456', description='connection password')

class LogCommonSettings(BaseModel) :
    level: str = Field(default='INFO', description='level of logging')
    @computed_field
    def level_logging(self) -> PositiveInt:
        return logger_level[self.level]
    to_file: bool = Field(default=False, description='file or console mode of the registrar')
    logs_folder_path: str = Field(default='.log', description='path to save log files')
    max_num_log_files: PositiveInt = Field(default=10, description='Maximum enabled number of log files')

class LogSpecificSettings(BaseModel) :
    name: str = Field(default='auto_app', description='name of logger')
    file_name_prefix: str = Field(default='log_', description='prefix of the log file name')

class LogSettings(BaseModel) :
    common: LogCommonSettings = Field(description='general section for logging settings')
    db_creating: LogSpecificSettings = Field(description='the logging settings section for the database initiation stage')
    generating: LogSpecificSettings = Field(description='the logging settings section for the sales generation stage')
    uploading: LogSpecificSettings = Field(description='the logging settings section for the stage of uploading sales '
                                                     'to the database')

# Domain settings
class StoreSettings(BaseModel) :
    cash_registers: list[int] = Field(description='the number of cash registers for each store in the chain of stores')
    ranks: list[int] = Field(description='the store`s rating by popularity among customers in the store chain')
    opening_hours: list[list[int]] = Field(description='opening hours of each store in the chain of stores')

class PriceDistributionsSettings(BaseModel) :
    range_prices: list[int] = Field(description='minimum and maximum prices in chain stores')
    mean_price: int = Field(default=1500, description='average price in chain stores')

class DiscountsSettings(BaseModel) :
    min_discount_price: int = Field(default=500, description='the minimum price value when the discount can be applied')
    discounts_values: list[float] = Field(description='available values of discounts')
    discounts_probs: list[float] = Field(description='values of the probabilities of occurrence of each discount')

class GoodsSettings(BaseModel) :
    categories: list[str] = Field(description='the number of cash registers for each store in the chain of stores')
    name_prefix: list[str] = Field(description='the store`s rating by popularity among customers in the store chain')
    category_capacity: list[int] = Field(description='opening hours of each store in the chain of stores')
    price_distribution: PriceDistributionsSettings =  Field(description='settings of the goods prices')
    discounts: DiscountsSettings = Field(description='settings of the discounts')

class StuffSettings(BaseModel) :
    range_of_manager_salary: list[int] = Field(description='the range of managers\' salaries')
    range_of_cashier_salary: list[int] = Field(description='the range of cashiers\' salaries')
    multiplicity_of_the_salary_sum: int = Field(default=50, gt=1, le=10000, description='multiplicity of the salary sum')

class StoreChainSettings(BaseModel) :
    stores: StoreSettings = Field(description='settings of the stores')
    goods: GoodsSettings = Field(description='product settings')
    stuff: StuffSettings = Field(description='salary ranges')
    range_of_chain_daily_load: list[float] = Field(description='the range of loads on the retail network of stores')
    range_of_cash_regs_daily_load: list[float] = Field(description='the range of cash registers loads')
    min_sec_per_cash_transaction: int = Field(default=120, gt=0, description='minimum time per cash transaction')

class AppSettings(BaseModel):
    database_connection: DBConnectionSettings = Field(description='data base connection settings')
    logging: LogSettings = Field(description='logging settings')
    store_chain: StoreChainSettings = Field(description='settings for the retail chain of stores')
    sales_storing_path: str = Field(default='data', description='folder for storing sales data')


dir_name = PurePath(__file__).parent


_settings_json_string = Path(PurePath.joinpath(dir_name, 'config.json')).read_text(encoding='utf-8')
settings = AppSettings.model_validate_json(_settings_json_string)

if __name__ == "__main__":
    print(_settings_json_string)
    print(settings.model_dump())