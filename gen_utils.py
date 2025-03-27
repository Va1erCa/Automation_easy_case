# A module with auxiliary utilities for generating sales.

import pandas as pd
from pathlib import Path, PurePath

import logger as log
from config_py import settings, dir_name


def _check_path(path_save: str) -> None:
    '''
    A simple function to check and create a folder using the specified path.
    :param path_save: the path being checked
    :return: None
    '''
    path = PurePath.joinpath(dir_name, path_save)
    if not Path(path).is_dir() :
        # Creating a folder if it doesn't exist yet
        Path.mkdir(path)


def _save_to_csv(df: pd.DataFrame, path_save: str, name: str) -> bool :
    '''
    Auxiliary function for saving a dataframe to a file
    :param df: the data frame for saving
    :param path_save: the path to save
    :param name: the name of the "csv" file where the date frame will be saved (only name)
    :return: a boolean value is an indicator of the operation's success.
    '''
    path = PurePath.joinpath(dir_name, path_save)
    try:
        df.to_csv(PurePath.joinpath(path, name), index=False)
    except Exception as e:
        log.logger.error(f'An error has occurred: {e}')
        return False

    return True


def post_process_df(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Auxiliary function for additional processing of the final data frame
    :param df: the data frame for processing
    :return: modified dataframe
    '''
    map_categories = pd.Series(settings.store_chain.goods.categories)
    map_name_prefix = pd.Series(settings.store_chain.goods.name_prefix)

    # Adding the required "item" field to the data frame by encoding it with the map function
    df['item'] = df['category_key'].map(map_name_prefix) + df['item_key'].astype('str')

    # Adding the required "category" field to the data frame by encoding it with the map function
    df['category'] = df['category_key'].map(map_categories)

    # We leave the necessary fields
    res_columns = (
        ['id_store', 'id_cash_reg', 'doc_id', 'item', 'category', 'amount', 'price', 'discount', 'receipt_time']
    )
    df_res = df.loc[:, res_columns]

    return df_res


def save_by_units(df: pd.DataFrame, path_save: str) -> None:
    '''
    The function of saving sales files for stores and cash registers.
    Each file name will look like this: <storage number>_<cache registry number>.csv
    :param df: the data frame for saving
    :param path_save: the path to save
    :return: None
    '''

    stores = df['id_store'].unique()
    cash_regs = df['id_cash_reg'].unique()

    # Setting a multi-index
    df = df.set_index(keys=['id_store', 'id_cash_reg'])

    # Using a multi-index, we quickly filter records for each file.
    for s in stores :
        for cr in cash_regs :
            try :
                df_chunk = df.loc[s, cr][:]
                if _save_to_csv(df=df_chunk, path_save=path_save, name=f'{s}_{cr}.csv') :
                    log.logger.info(
                        f'The sales history of cash register No. {cr} from store No. {s} has been successfully '
                        f'saved in the file "{s}_{cr}.csv".'
                    )
                else :
                    log.logger.info(
                        f'The sales history of cash register No. {cr} from store No. {s} has not been saved!'
                    )

            except KeyError as e :
                break
