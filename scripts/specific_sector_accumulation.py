import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def sector_specific_accumulation(sector_name, sector_specific_data, trading_days=5, top_n=20):
    """
    Plot cumulative volume for top `n` tickers over the last `trading_days` trading days.
    
    Parameters:
    - sector_specific_data (DataFrame): DataFrame with 'Date', 'Ticker', and 'Volume' columns.
    - trading_days (int): Number of most recent trading days to include.
    - top_n (int): Number of top tickers to display.
    """
    sector_specific_data = sector_specific_data[sector_specific_data["Sector"] == sector_name].copy()
    # Ensure 'Date' is datetime and sort
    sector_specific_data['Date'] = pd.to_datetime(sector_specific_data['Date'])
    sector_specific_data = sector_specific_data.sort_values('Date')
    sector_specific_data = sector_specific_data[sector_specific_data["Ticker"]!= 'Nepse Index']

    # Pivot table to get turnover
    pivot_table_vol = pd.pivot_table(
        sector_specific_data,
        values="Turnover",
        index="Date",
        columns="Ticker",
        fill_value=0
    )

    # Keep only the last N trading days
    pivot_table_vol = pivot_table_vol.tail(trading_days)

    # Calculate cumulative volume
    cumulative_volume = pivot_table_vol.cumsum()

    # Get top tickers by latest cumulative volume
    latest_volumes = cumulative_volume.iloc[-1]
    top_tickers = latest_volumes.sort_values(ascending=False).head(top_n)
    time_series_top = cumulative_volume[top_tickers.index]

    # Plotting
    fig = make_subplots(specs=[[{"secondary_y": False}]])

    for ticker in time_series_top.columns:
        fig.add_trace(go.Scatter(
            x=time_series_top.index,
            y=time_series_top[ticker],
            mode='lines+markers',
            name=ticker,
        ))

        # Add annotation for the last point
        fig.add_annotation(
            x=time_series_top.index[-1] + pd.Timedelta(days=1),
            y=time_series_top[ticker].iloc[-1],
            text=ticker,
            showarrow=False,
            font=dict(size=10),
            xanchor='left',
            yanchor='middle',
        )

    fig.update_layout(
        title=f"{sector_name} Top Turnover Over the Last {trading_days} Trading Days",
        xaxis_title="Date",
        yaxis_title="Cumulative Volume",
        width=1200,
        height=700,
        showlegend=False,
        xaxis=dict(
            tickformat="%b %d",  # Format: e.g., "May 16"
            tickangle=45,
            tickmode='auto',
            nticks=10,
            showgrid=True,
            showline=True
        )
    )

    fig.show()