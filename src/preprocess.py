import pandas as pd

def load_data(path):
    return pd.read_csv(path)


def clean_data(df):
    # Convert dates
    # Dataset stores dates as DD/MM/YYYY (for example 15/04/2018).
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%d/%m/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%d/%m/%Y')

    # Feature engineering
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.month_name()
    df['Quarter'] = df['Order Date'].dt.quarter

    # Drop unnecessary
    if 'Postal Code' in df.columns:
        df = df.drop(columns=['Postal Code'])

    df = df.drop_duplicates()
    df = df.dropna()

    return df


def save_cleaned(df, path):
    df.to_csv(path, index=False)