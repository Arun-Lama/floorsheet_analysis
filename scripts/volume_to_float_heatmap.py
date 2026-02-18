import numpy as np
import pandas as pd
from datetime import timedelta
import plotly.express as px

def plot_relative_turnover_heatmap(adjusted_price, float_data, top_n=20, timeframes=None):
    """
    Computes and plots a heatmap of relative turnover (volume / free float) 
    for the top N tickers across given timeframes.

    Parameters:
        adjusted_price (pd.DataFrame): Must contain 'Date', 'Ticker', 'Volume'.
        float_data (pd.DataFrame): Must contain 'Symbol' and 'Floated Shares'.
        top_n (int): Number of top tickers to include based on longest timeframe.
        timeframes (dict): Optional custom timeframes, default is {'1D': 1 day, '1W': 1 week}.
    """
    # Default timeframes if not provided
    if timeframes is None:
        today = adjusted_price['Date'].max()
        timeframes = {
            '1D': today - timedelta(days=1),
            '1W': today - timedelta(weeks=1)
        }

    # Step 1: Prepare floated shares
    floated_series = float_data.set_index('Symbol')['Floated Shares']

    # Step 2: Pivot volume data
    traded_shares = adjusted_price[['Date', 'Ticker', 'Volume']]
    volume_pivot = traded_shares.pivot(index='Date', columns='Ticker', values='Volume').fillna(0)

    # Step 3: Compute turnover for each timeframe
    today = volume_pivot.index.max()
    turnover_data = {}

    for label, start_date in timeframes.items():
        if start_date > today:
            raise ValueError(f"Start date for timeframe '{label}' is after latest date in data.")
        period_volume = volume_pivot.loc[start_date:today].sum()
        turnover = period_volume / floated_series
        turnover_data[label] = turnover

    # Step 4: Combine into DataFrame
    turnover_df = pd.DataFrame(turnover_data)
    turnover_df.dropna(how='all', inplace=True)

    # Step 5: Sort by longest timeframe for top_n
    last_period = list(timeframes.keys())[-1]
    turnover_df_sorted = turnover_df.sort_values(by=last_period, ascending=False).head(top_n).dropna()

    # Step 6: Plot heatmap
    fig = px.imshow(
        turnover_df_sorted,
        text_auto='.2f',
        color_continuous_scale='Blues',
        aspect='auto',
        title=f'Top {top_n} Stocks - Relative Turnover Heatmap (Volume / Float)'
    )
    fig.update_layout(
        xaxis_title='Period',
        yaxis_title='Ticker',
        height=600
    )
    fig.show()
