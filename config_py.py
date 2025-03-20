from datetime import datetime
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

class LogSettings(BaseModel) :
    name: str = Field(default='auto_app', description='name of logger')
    level: str = Field(default='INFO', description='level of logging')
    @computed_field
    def level_logging(self) -> PositiveInt:
        return logger_level[self.level]
    to_file: bool = Field(default=False, description='file or console mode of the registrar')
    logs_folder_path: str = Field(default='.log', description='path to save log files')
    file_name_prefix: str = Field(default='log_', description='prefix of the log file name')
    max_num_log_files: PositiveInt = Field(default=10, description='Maximum enabled number of log files')

# Domain settings
class StoreSettings(BaseModel) :
    cash_registers: list[int] = Field(description='the number of cash registers for each store in the chain of stores')
    ranks: list[int] = Field(description='the store`s rating by popularity among customers in the store chain')
    opening_hours: list[list[int]] = Field(description='opening hours of each store in the chain of stores')

class GoodsSettings(BaseModel) :
    categories: list[str] = Field(description='the number of cash registers for each store in the chain of stores')
    name_prefix: list[str] = Field(description='the store`s rating by popularity among customers in the store chain')
    category_capacity: list[int] = Field(description='opening hours of each store in the chain of stores')

class StoreChainSettings(BaseModel) :
    stores: StoreSettings = Field(description='settings of the stores')
    goods: GoodsSettings = Field(description='product settings')
    range_of_chain_daily_load: list[float] = Field(description='the range of loads on the retail network of stores')
    range_of_cash_regs_load: list[float] = Field(description='the range of cashier loads')
    min_sec_per_cash_transaction: int = Field(default=120, description='minimum time per cash transaction')

class AppSettings(BaseModel):
    database_connection: DBConnectionSettings = Field(description='data base connection settings')
    logging_generating: LogSettings = Field(description='logging settings for the task of generating sales data')
    logging_uploading: LogSettings = Field(description='logging settings for the task of uploading sales data to the database')
    store_chain: StoreChainSettings = Field(description='settings for the retail chain of stores')
    sales_storing_path: str = Field(default='data', description='folder for storing sales data')


dir_name = PurePath(__file__).parent


_settings_json_string = Path(PurePath.joinpath(dir_name, 'config.json')).read_text(encoding='utf-8')
settings = AppSettings.model_validate_json(_settings_json_string)

if __name__ == "__main__":
    print(_settings_json_string)
    print(settings.model_dump())