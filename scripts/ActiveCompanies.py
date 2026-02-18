import pandas as pd
import requests



def stock_and_indices_data():
    url = "https://raw.githubusercontent.com/Arun-Lama/active_companies_list/main/companies.json"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    active_companies_df = df
    two_cols = active_companies_df[['symbol', 'sectorName']]
    two_cols.rename(columns= {"symbol": "Ticker", "sectorName": "Sector"}, inplace = True)

    indices_df = pd.DataFrame({
        "Ticker": [
            "Banking SubIndex", "Development Bank Index", "Finance Index",
            "Hotels And Tourism", "HydroPower Index", "Investment",
            "Life Insurance", "Manufacturing And Processing", "Microfinance Index",
            "Mutual Fund", "Non Life Insurance", "Others Index",
            "Trading Index", "Nepse Index"
        ],
        "Sector": "Index"
        })

    return pd.concat(
            [two_cols, indices_df], axis = 0
            )
