def get_all_daily_floorsheet_data():
    import os
    import requests
    import pandas as pd
    from dotenv import load_dotenv

    load_dotenv()

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

    OWNER = "Arun-Lama"
    REPO = "floorsheet_automation"
    PATH = "daily_floorsheet"

    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    files = response.json()
    dfs = []

    for file in files:
        if file["name"].endswith(".csv"):
            raw_url = file["download_url"]

            df = pd.read_csv(raw_url, index_col=0)
            df.index.name = "Date"
            # df.reset_index(inplace=True)

            dfs.append(df)

    if not dfs:
        raise ValueError("No CSV files found in the directory.")

    final_df = pd.concat(dfs, ignore_index=True)

    final_df["Date"] = pd.to_datetime(final_df["Date"])
    final_df.sort_values("Date", inplace=True)

    return final_df
