import pandas as pd 
import numpy as np

def get_adjusted_price_of_all_companies():
    import os
    import requests
    import io
    from dotenv import load_dotenv
    
    load_dotenv()
    
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    url = (
        "https://raw.githubusercontent.com/"
        "Arun-Lama/Adjusted-price-to-sheet/main/"
        "adjusted price/all_adj_companies_data.csv"
    )
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    df = pd.read_csv(io.StringIO(response.text))
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values(by = ['Date'], ascending = True, inplace = True) 
    return clean_price_data(df)

def clean_price_data(df: pd.DataFrame) -> pd.DataFrame:
    price_cols = ["Open", "High", "Low", "Close"]

    df = df.copy()
    df[price_cols] = df[price_cols].replace(0, np.nan)
    df = df.dropna(subset=["Open", "Close"])
    df = df[(df[price_cols] > 0).all(axis=1)]

    return df
