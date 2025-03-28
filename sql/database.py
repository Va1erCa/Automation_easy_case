# database module

import logger as log

from pgdb import Database, Row, Rows
from config_py import settings

async def recreate_tables() -> bool:
    db: Database = Database(settings.database_connection)
    if not db.is_connected :
        return False

    if not db.create_table(table_name='channel',
                           columns_statement='''
                                id int8 NOT NULL,
                                username varchar NOT NULL,
                                title varchar NOT NULL,
                                category varchar NULL,
                                creation_time timestamp NULL,
                                turn_on_time timestamp NULL,
                                turn_off_time timestamp NULL,
                                CONSTRAINT channel_pk PRIMARY KEY (id)
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='channel_hist',
                           columns_statement='''
                                channel_id int8 NOT NULL,
                                update_time timestamp NOT NULL,
                                subscribers int4 NULL,
                                msgs_count int4 NULL,
                                CONSTRAINT channel_hist_channel_fk FOREIGN KEY (channel_id) 
                                    REFERENCES public.channel(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='channel_plan',
                           columns_statement='''
                                planned_at timestamp NOT NULL,
                                completed_at timestamp NULL
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='post',
                           columns_statement='''
                                channel_id int8 NOT NULL,
                                post_id int4 NOT NULL,
                                forward_from_chat int8 NULL,
                                creation_time timestamp NOT NULL,
                                drop_time timestamp NULL,
                                is_advertising bool DEFAULT false NOT NULL,
                                media_group_id int8 NULL,
                                media_type varchar NULL,
                                post_text varchar NULL,
                                text_len int4 NULL,
                                text_entities_count int4 NULL,
                                post_url varchar NULL,
                                is_planned bool DEFAULT false NOT NULL,
                                CONSTRAINT post_pk PRIMARY KEY (channel_id, post_id),
                                CONSTRAINT post_unique UNIQUE (media_group_id),
                                CONSTRAINT post_channel_fk FOREIGN KEY (channel_id) 
                                    REFERENCES public.channel(id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='post_hist',
                           columns_statement='''
                                channel_id int8 NOT NULL,
                                post_id int4 NOT NULL,
                                update_time timestamp NOT NULL,
                                observation_day int4 NOT NULL, 
                                post_comments int4 DEFAULT 0 NOT NULL,
                                post_views int4 DEFAULT 0 NOT NULL,
                                stars int4 DEFAULT 0 NOT NULL,
                                positives int4 DEFAULT 0 NOT NULL,
                                negatives int4 DEFAULT 0 NOT NULL,
                                neutrals int4 DEFAULT 0 NOT NULL,
                                customs int4 DEFAULT 0 NOT NULL,
                                reposts int4 DEFAULT 0 NOT NULL,
                                CONSTRAINT post_hist_post_fk FOREIGN KEY (channel_id, post_id)
                                    REFERENCES public.post(channel_id, post_id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='media_group',
                           columns_statement='''                            
                                media_group_id int8 NOT NULL,
                                update_time timestamp NOT NULL,
                                post_id int4 NOT NULL,
                                observation_day int4 NOT NULL,
                                post_order int2 NOT NULL,
                                post_views int4 DEFAULT 0 NOT NULL,
                                reposts int4 DEFAULT 0 NOT NULL,
                                CONSTRAINT media_group_post_fk FOREIGN KEY (media_group_id) 
                                    REFERENCES public.post(media_group_id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    if not db.create_table(table_name='task_plan',
                           columns_statement='''
                                channel_id int8 NOT NULL,
                                post_id int4 NOT NULL,
                                observation_day int4 NOT NULL,
                                planned_at timestamp NOT NULL,
                                completed_at timestamp NULL,
                                CONSTRAINT task_fk FOREIGN KEY (channel_id, post_id)
                                    REFERENCES public.post(channel_id, post_id) ON UPDATE CASCADE
                                ''',
                           overwrite=True) : return False

    return True


if __name__ == '__mail__' :
    pass