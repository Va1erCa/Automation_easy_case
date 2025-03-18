from datetime import datetime
from pathlib import Path, PurePath
from pydantic import BaseModel, Field, PositiveInt, computed_field


class DBConnectionSettings(BaseModel) :
    host: str = Field(default='localhost', description='connection host')
    port: PositiveInt = Field(default=5432, description='connection port')
    dbname: str = Field(default='household_goods_chain', description='connection data base name')
    user: str = Field(default='postgres', description='connection user')
    password: str = Field(default='123456', description='connection password')

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

class AppSettings(BaseModel):
    database_connection: DBConnectionSettings = Field(description='data base connection settings')
    store_chain: StoreChainSettings = Field(description='settings for the retail chain of stores')


dir_name = PurePath(__file__).parent

_settings_json_string = Path(PurePath.joinpath(dir_name, 'config.json')).read_text(encoding='utf-8')
settings = AppSettings.model_validate_json(_settings_json_string)

if __name__ == "__main__":
    print(settings.model_dump())