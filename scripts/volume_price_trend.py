import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_and_plot_vpt(data: pd.DataFrame, data_type: str = "indices", trading_days: int = 300, sector_name: str = None):
    """
    Calculates and plots Volume Price Trend (VPT) for stocks (with optional sector) or indices.

    Parameters:
    - data: DataFrame with columns ['Date', 'Ticker', 'Close', 'Volume' or 'Turnover']
             and 'Sector' if filtering stocks
    - data_type: 'stocks' or 'indices'
    - trading_days: Number of most recent trading days to include
    - sector_name: Sector name to filter if data_type is 'stocks'

    Returns:
    - vpt: DataFrame of raw VPT values
    """
    assert data_type in ['stocks', 'indices'], "data_type must be 'stocks' or 'indices'"
    volume_col = 'Turnover' if data_type == 'stocks' else 'Volume'

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    # Optional sector filter
    if data_type == 'stocks' and sector_name:
        if 'Sector' not in data.columns:
            raise ValueError("Data must include 'Sector' column to filter by sector.")
        data = data[data['Sector'] == sector_name]

    if data.empty:
        raise ValueError("Filtered data is empty. Check your sector name or input data.")

    # Pivot Close and Volume
    pivot_close = pd.pivot_table(data, values="Close", index="Date", columns="Ticker", fill_value=0)
    pivot_volume = pd.pivot_table(data, values=volume_col, index="Date", columns="Ticker", fill_value=0)

    # Only use actual trading days
    pivot_close = pivot_close.tail(trading_days)
    pivot_volume = pivot_volume.loc[pivot_close.index]  # Align to avoid mismatches

    # Daily returns
    daily_return = pivot_close.pct_change().fillna(0)

    # VPT: Volume × Daily Return
    vpt_change = pivot_volume * daily_return
    vpt = vpt_change.cumsum().fillna(0)


    # Plot
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    for ticker in vpt.columns:
        fig.add_trace(go.Scatter(
            x=vpt.index.strftime('%Y-%m-%d'),
            y=vpt[ticker],
            mode='lines+markers',
            name=ticker
        ))

        # Label the last point
        fig.add_annotation(
            x=vpt.index[-1].strftime('%Y-%m-%d'),
            y=vpt[ticker].iloc[-1],
            text=ticker,
            showarrow=False,
            font=dict(size=10),
            xanchor='left',
            yanchor='middle',
        )

    fig.update_layout(
        title=f"Volume Price Trend (VPT) - Last {trading_days} Days ({data_type.capitalize()})" + (f" – Sector: {sector_name}" if sector_name else ""),
        xaxis_title="Date",
        yaxis_title="VPT",
        xaxis=dict(type='category'),
        width=1200,
        height=700,
        showlegend=False
    )

    fig.show()

def stock_wise_VPT(data: pd.DataFrame, data_type: str = "indices", trading_days: int = 300, sector_name: str = None):
    """
    Calculates and plots Volume Price Trend (VPT) for stocks (with optional sector) or indices.

    Parameters:
    - data: DataFrame with columns ['Date', 'Ticker', 'Close', 'Volume' or 'Turnover']
             and 'Sector' if filtering stocks
    - data_type: 'stocks' or 'indices'
    - trading_days: Number of most recent trading days to include
    - sector_name: Sector name to filter if data_type is 'stocks'

    Returns:
    - vpt: DataFrame of raw VPT values
    """
    assert data_type in ['stocks', 'indices'], "data_type must be 'stocks' or 'indices'"
    volume_col = 'Turnover' if data_type == 'stocks' else 'Volume'

    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    # Optional sector filter
    if data_type == 'stocks' and sector_name:
        if 'Sector' not in data.columns:
            raise ValueError("Data must include 'Sector' column to filter by sector.")
        data = data[data['Sector'] == sector_name]

    if data.empty:
        raise ValueError("Filtered data is empty. Check your sector name or input data.")

    # Pivot Close and Volume
    pivot_close = pd.pivot_table(data, values="Close", index="Date", columns="Ticker", fill_value=0)
    pivot_volume = pd.pivot_table(data, values=volume_col, index="Date", columns="Ticker", fill_value=0)

    # Only use actual trading days
    pivot_close = pivot_close.tail(trading_days)
    pivot_volume = pivot_volume.loc[pivot_close.index]  # Align to avoid mismatches

    # Daily returns
    daily_return = pivot_close.pct_change().fillna(0)

    # VPT: Volume × Daily Return
    vpt_change = pivot_volume * daily_return
    vpt = vpt_change.cumsum().fillna(0)
    vpt = vpt[vpt.iloc[-1].sort_values(ascending=False).head(10).index]


    # Plot
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    for ticker in vpt.columns:
        fig.add_trace(go.Scatter(
            x=vpt.index.strftime('%Y-%m-%d'),
            y=vpt[ticker],
            mode='lines+markers',
            name=ticker
        ))

        # Label the last point
        fig.add_annotation(
            x=vpt.index[-1].strftime('%Y-%m-%d'),
            y=vpt[ticker].iloc[-1],
            text=ticker,
            showarrow=False,
            font=dict(size=10),
            xanchor='left',
            yanchor='middle',
        )

    fig.update_layout(
        title=f"Volume Price Trend (VPT) - Last {trading_days} Days ({data_type.capitalize()})" + (f" – Sector: {sector_name}" if sector_name else ""),
        xaxis_title="Date",
        yaxis_title="VPT",
        xaxis=dict(type='category'),
        width=1200,
        height=700,
        showlegend=False
    )

    fig.show()



def plot_close_vs_cum_turnover(data: pd.DataFrame, ticker: str, trading_days: int = 300):
    """
    Plots Closing Price against Cumulative Turnover for a given stock.

    Parameters:
    - data: DataFrame with ['Date', 'Ticker', 'Close', 'Turnover']
    - ticker: Ticker symbol to analyze
    - trading_days: Number of most recent trading days to include

    Returns:
    - DataFrame with ['Date', 'CumulativeTurnover', 'Close']
    """
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date')

    stock_data = data[data['Ticker'] == ticker].copy()
    if stock_data.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    stock_data = stock_data.tail(trading_days)
    stock_data['CumulativeTurnover'] = stock_data['Turnover'].cumsum()

    # Plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Cumulative Turnover on primary y-axis
    fig.add_trace(go.Scatter(
        x=stock_data['Date'].dt.strftime('%Y-%m-%d'),
        y=stock_data['CumulativeTurnover'],
        mode='lines+markers',
        name="Cumulative Turnover",
        line=dict(color='blue')
    ), secondary_y=False)

    # Close on secondary y-axis
    fig.add_trace(go.Scatter(
        x=stock_data['Date'].dt.strftime('%Y-%m-%d'),
        y=stock_data['Close'],
        mode='lines+markers',
        name="Close Price",
        line=dict(color='orange', dash='dot')
    ), secondary_y=True)

    fig.update_layout(
        title=f"{ticker} - Closing Price vs Cumulative Turnover (Last {trading_days} Days)",
        xaxis_title="Date",
        yaxis_title="Cumulative Turnover",
        width=1100,
        height=650,
        legend=dict(x=0.01, y=0.99)
    )

    fig.update_yaxes(title_text="Cumulative Turnover", secondary_y=False)
    fig.update_yaxes(title_text="Close Price", secondary_y=True)

    fig.show()

