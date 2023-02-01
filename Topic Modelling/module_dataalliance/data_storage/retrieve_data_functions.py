import os
import pandas as pd


def retrieve_twitter_data():
    # Returns the twitter data as a dataframe
    df = pd.read_parquet(os.getcwd() + '/data_storage/data/twitter_data.parquet.gzip')

    return df


def retrieve_newspaper_data():
    # Returns the newspapers data as a dataframe
    df = pd.read_parquet(os.getcwd() + '/data_storage/data/newspaper_data.parquet.gzip')

    return df