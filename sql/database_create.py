# The module for the first initialization of the database of our store chain

from pgdb import Database, Row, Rows
from config_py import settings

import logger as log
from logger import set_logger

log.logger = set_logger(log_set=settings.logging_uploading)


def recreate_tables() -> bool:
    db: Database = Database(settings.database_connection)
    if not db.is_connected :
        return False

    if not db.create_table(table_name='stuff',
                           columns_statement='''
                                id int4 NOT NULL,
                                first_name varchar NOT NULL,
                                middle_name varchar NULL,
                                last_name varchar NOT NULL,
                                salary numeric NULL,
                                phone varchar NULL,
                                CONSTRAINT stuff_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='store',
                           columns_statement='''
                                id int4 NOT NULL,
                                store_name varchar NOT NULL,
                                opening_hour varchar NOT NULL,
                                closing_hour varchar NOT NULL,
                                address varchar NOT NULL,
                                phone varchar NOT NULL,
                                director int4 NOT NULL,
                                CONSTRAINT store_pk PRIMARY KEY (id),
                                CONSTRAINT store_stuff_fk FOREIGN KEY (director) 
                                    REFERENCES public.stuff(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='cash_register',
                           columns_statement='''
                                id int4 NOT NULL,
                                store_id int4 NOT NULL,
                                cashier int4 NOT NULL,
                                CONSTRAINT cash_register_pk PRIMARY KEY (id, store_id),
                                CONSTRAINT cash_register_stuff_fk FOREIGN KEY (cashier) 
                                    REFERENCES public.stuff(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='category',
                           columns_statement='''
                                id int4 NOT NULL,
                                category_name varchar NULL,
                                CONSTRAINT category_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='discount',
                           columns_statement='''                            
                                id int4 NOT NULL,
                                value numeric NOT NULL,
                                promo_action varchar NULL,
                                CONSTRAINT discount_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='goods',
                           columns_statement='''
                                id int4 NOT NULL,
                                item_name varchar NOT NULL,
                                category_id int4 NOT NULL,
                                price numeric NOT NULL,
                                discount_id int4 NOT NULL,
                                purchase_price numeric NULL,
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


if __name__ == '__main__' :

    print(recreate_tables())