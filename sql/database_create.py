# The module for the first initialization and filling in of the database of our store chain

from datetime import datetime
import re, random
from faker import Faker
from string import ascii_uppercase, ascii_lowercase

from config_py import settings
import logger as log
from logger import set_logger

log.logger = set_logger(log_common_set=settings.logging.common, log_specific_set=settings.logging.db_creating)

from pgdb import Database, Rows, DBQueryResult
from exceptions import AppDBError
from chain_stores import goods
from app_types import DBCategory, DBDiscount, DBGoods, DBStuff, DBStore, DBCashRegister


def recreate_tables() -> bool:
    db: Database = Database(settings.database_connection)
    if not db.is_connected :
        return False

    if not db.create_table(table_name='stuff',
                           columns_statement='''
                                id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
                                first_name varchar NOT NULL,
                                middle_name varchar NULL,
                                last_name varchar NOT NULL,
                                salary int4 NOT NULL,
                                phone varchar NULL,
                                CONSTRAINT stuff_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='store',
                           columns_statement='''
                                id int4 NOT NULL,
                                store_name varchar NOT NULL,
                                opening_hour int4 NOT NULL,
                                closing_hour int4 NOT NULL,
                                address varchar NOT NULL,
                                phone varchar NOT NULL,
                                manager int4 NOT NULL,
                                CONSTRAINT store_pk PRIMARY KEY (id),
                                CONSTRAINT store_stuff_fk FOREIGN KEY (manager) 
                                    REFERENCES public.stuff(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='cash_register',
                           columns_statement='''
                                id int4 NOT NULL,
                                store_id int4 NOT NULL,
                                cr_receipt_code varchar(2) NOT NULL,
                                cashier int4 NOT NULL,                                
                                CONSTRAINT cash_register_pk PRIMARY KEY (id, store_id),
                                CONSTRAINT cash_register_stuff_fk FOREIGN KEY (cashier) 
                                    REFERENCES public.stuff(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='category',
                           columns_statement='''
                                id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,                                
                                category_name varchar NULL,
                                CONSTRAINT category_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='discount',
                           columns_statement='''                            
                                id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
                                value numeric(4, 2) NOT NULL,
                                promo_action varchar NULL,
                                CONSTRAINT discount_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='goods',
                           columns_statement='''
                                id int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
                                item_name varchar NOT NULL,
                                category_id int4 NOT NULL,
                                price numeric(10, 2) NOT NULL,
                                discount_id int4 NOT NULL,
                                purchase_price numeric(10, 2) NULL,
                                CONSTRAINT goods_pk PRIMARY KEY (id),
                                CONSTRAINT goods_category_fk FOREIGN KEY (category_id) 
                                    REFERENCES public.category(id) ON UPDATE CASCADE,
                                CONSTRAINT goods_discount_fk FOREIGN KEY (discount_id) 
                                    REFERENCES public.discount(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='receipt',
                           columns_statement='''
                                id varchar NOT NULL,
                                receipt_time timestamp NOT NULL,
                                store_id int4 NOT NULL,
                                cash_reg_id int4 NOT NULL,
                                CONSTRAINT receipt_pk PRIMARY KEY (id),
                                CONSTRAINT receipt_cash_register_fk FOREIGN KEY (cash_reg_id,store_id) 
                                    REFERENCES public.cash_register(id,store_id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='receipt_line',
                           columns_statement='''
                                id int4 NOT NULL,
                                id_receipt varchar NOT NULL,
                                id_item int4 NOT NULL,
                                amount int4 NOT NULL,
                                CONSTRAINT receipt_line_pk PRIMARY KEY (id, id_receipt),
                                CONSTRAINT receipt_line_goods_fk FOREIGN KEY (id_item) 
                                    REFERENCES public.goods(id) ON UPDATE CASCADE,
                                CONSTRAINT receipt_line_receipt_fk FOREIGN KEY (id_receipt) 
                                    REFERENCES public.receipt(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    return True


def get_new_phone_number(fake: Faker) -> str:
    phone_digits = ''.join(re.findall(r'\d+', fake.phone_number()))
    new_phone = f'+7 {phone_digits[1 :4]} {phone_digits[4 :7]} {phone_digits[7 :]}'
    return new_phone


def add_new_employee(db: Database, fake: Faker, salary_range: tuple) -> int :
    if random.randint(0, 1) :
        first_name, middle_name, last_name = fake.first_name_male(), fake.middle_name_male(), fake.last_name_male()
    else :
        first_name, middle_name, last_name = fake.first_name_female(), fake.middle_name_female(), fake.last_name_female()
    salary = random.randrange(*salary_range, settings.store_chain.stuff.multiplicity_of_the_salary_sum)
    values: Rows = (
        DBStuff(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            salary=salary,
            phone=get_new_phone_number(fake=fake)
        ),
    )
    res = fill_in_one_table(
        db=db,
        table_name='stuff',
        values=values,
        insert_fields=DBStuff._fields,
        returning_field='id',
        mute=True)

    return res.value[0][0]


def fill_in_one_table(
        db: Database,
        table_name: str,
        values: Rows,
        insert_fields: tuple | None=None,
        returning_field: str | None=None,
        mute: bool=False
) -> DBQueryResult :

    res = db.insert_rows(
        table_name=table_name,
        insert_fields=insert_fields,
        values=values,
        returning_field=returning_field
    )

    if res.is_successful :
        if not mute:
            log.logger.info(f'The "{table_name}" table have been successfully filled.')
    else :
        raise AppDBError(f'Database operation error: couldn\'t filled in the table "{table_name}".')
    return res


def fill_in_tables() :
    db: Database = Database(settings.database_connection)
    if not db.is_connected :
        return False

    try:
        # initializing the Faker module
        Faker.seed(random.randint(0, 9999))
        fake = Faker('ru_RU')

        # filling in the table "category"
        values: Rows = tuple(
            DBCategory(category_name=cat) for cat in settings.store_chain.goods.categories
        )
        fill_in_one_table(db=db, table_name='category', values=values, insert_fields=DBCategory._fields)

        # filling in the table "discount"
        values: Rows = tuple(
            DBDiscount(value=vl, promo_action=f'promo_{vl}')
            for vl in settings.store_chain.goods.discounts.discounts_values
        )
        fill_in_one_table(db=db, table_name='discount', values=values, insert_fields=DBDiscount._fields)

        # filling in the table "goods"
        # encoding discounts
        discounts_dict = dict(
            zip(
                settings.store_chain.goods.discounts.discounts_values,
                range(1, len(settings.store_chain.goods.discounts.discounts_values)+1)
            )
        )
        values: Rows = tuple(
            DBGoods(
                item_name=f'{settings.store_chain.goods.name_prefix[item.category_key]}{item.item_key}',
                category_id=item.category_key+1,
                price=float(item.price),
                discount_id=discounts_dict.get(item.discount, 1),
                purchase_price=float(item.price * 0.7) )
            for item in goods.goods
        )
        fill_in_one_table(db=db, table_name='goods', values=values, insert_fields=DBGoods._fields)

        # filling in the table "store"
        values: Rows = tuple(
            DBStore(
                id=i,
                store_name=f'Магазин_{i}',
                opening_hour=opening_h[0],
                closing_hour=opening_h[1],
                address=fake.address(),
                phone=get_new_phone_number(fake=fake),
                manager=add_new_employee(db=db, fake=fake, salary_range=settings.store_chain.stuff.range_of_manager_salary)
            ) for i, opening_h in enumerate(settings.store_chain.stores.opening_hours, start=1)
        )
        fill_in_one_table(db=db, table_name='store', values=values)

        # filling in the table "cash_register"
        values: Rows = tuple(
            DBCashRegister(
                id=j,
                store_id=i,
                cr_receipt_code=ascii_uppercase[i-1] + ascii_lowercase[j-1],
                cashier=add_new_employee(db=db, fake=fake, salary_range=settings.store_chain.stuff.range_of_cashier_salary)
            ) for i, cash_regs in enumerate(settings.store_chain.stores.cash_registers, start=1)
            for j in range(1, cash_regs+1)
        )
        fill_in_one_table(db=db, table_name='cash_register', values=values)


        # filling in the table "stuff"
        # number_of_staff = len(settings.store_chain.stores.ranks) + sum(settings.store_chain.stores.cash_registers)
        #
        # for _ in range(number_of_staff) :
        #     add_new_employee(db=db, fake=fake, salary_range=settings.store_chain.stuff.range_of_cashier_salary)


    except AppDBError as e:
        log.logger.error(f'Error: {e}')
        return False

    return True


def main() :

    log.logger.info('The process of creating a Postgres database has been started.')

    time_start = datetime.now()

    if recreate_tables() and fill_in_tables() :
        log.logger.info(f'The process of creating and filling in the database has been completed successfully, '
                        f'execution time - {(datetime.now() - time_start).total_seconds():.2f} seconds.')
    else :
        log.logger.error(f'Unfortunately, the process of creating and filling in the database was not successful!')


if __name__ == '__main__' :
    main()