# Module for data types of the app

from datetime import datetime

from pgdb import Row, Rows


# The data structures for save in database
# Record in <category> table - product categories
class DBCategory(Row) :
    # id: int                 # category id (primary key) - autoincrement field
    category_name: str      # name of category

# Record in <discount> table - discounts applied in stores
class DBDiscount(Row) :
    # id: int                 # discount id (primary key) - autoincrement field
    value: float            # discount amount
    promo_action: str       # the name of the promotion for this discount

# Record in <goods> table - full list of goods of our chain stores
class DBGoods(Row) :
    #id: int                 # product ID (primary key) - autoincrement field
    item_name: str          # name of the product
    category_id: int        # product category ID
    price: float            # retail price
    discount_id: int        # discount id
    purchase_price: float   # purchase price

# Record in <stuff> table - list of employees of our store chain
class DBStuff(Row) :
    #id: int                 # stuff ID (primary key) - autoincrement field
    first_name: str         # employee's name
    middle_name: str        # employee's patronymic
    last_name: str          # employee's last name
    salary: int             # employee's salary
    phone: str              # employee's personal phone number

# Record in <store> table - list of stores of our store chain
class DBStore(Row) :
    id: int                 # store ID (primary key)
    store_name: str         # store name
    opening_hour: int       # the store's opening hour
    closing_hour: int       # the store's closing hour
    address: str            # store address
    phone: str              # store phone
    manager: int            # ID of store manager

# Record in <cash_register> table - list of stores of our store chain
class DBCashRegister(Row) :
    id: int                 # cash register ID (primary key)
    store_id: int           # store ID
    cr_receipt_code: str    # the code prefix that the cash register putting for it own receipts
    cashier: int            # ID of cashier employee
