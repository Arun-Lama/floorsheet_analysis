import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_cumulative_returns_by_trading_days(all_stock_data, trading_days=5, top_n=20):
    """
    Plot cumulative returns for top `n` tickers over the last `trading_days` trading days.

    Parameters:
    - all_stock_data (DataFrame): DataFrame with 'Date', 'Ticker', 'Close'.
    - trading_days (int): Number of most recent trading days to include.
    - top_n (int): Number of top tickers to display.
    """

    # Ensure 'Date' is datetime and sort
    all_stock_data['Date'] = pd.to_datetime(all_stock_data['Date'])
    all_stock_data = all_stock_data.sort_values('Date')

    # Pivot closing prices by date and ticker
    pivot_close = pd.pivot_table(
        all_stock_data,
        values="Close",
        index="Date",
        columns="Ticker",
        aggfunc="last"
    )

    # Keep only last `trading_days` rows
    pivot_close = pivot_close.tail(trading_days)

    # Calculate log returns
    log_returns = np.log(pivot_close / pivot_close.shift(1))

    # Calculate cumulative log returns and convert to percentage
    cumulative_returns = log_returns.cumsum().apply(np.exp) - 1
    cumulative_returns *= 100  # to percentage
    latest_returns = cumulative_returns.iloc[-1]

    # Select top N performing tickers
    top_tickers = latest_returns.sort_values(ascending=False).head(top_n).index
    top_cum_returns = cumulative_returns[top_tickers]

    # Plotting
    fig = make_subplots()

    for ticker in top_tickers:
        fig.add_trace(go.Scatter(
            x=top_cum_returns.index,
            y=top_cum_returns[ticker],
            mode='lines+markers',
            name=ticker,
        ))

        fig.add_annotation(
            x=top_cum_returns.index[-1] + pd.Timedelta(days=1),
            y=top_cum_returns[ticker].iloc[-1],
            text=ticker,
            showarrow=False,
            font=dict(size=10),
            xanchor='left',
            yanchor='middle',
        )

    fig.update_xaxes(range=[top_cum_returns.index.min(), top_cum_returns.index.max()])

    fig.update_layout(
        title=f"Cumulative Returns (%) for Top {top_n} Stocks Over Last {trading_days} Trading Days",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        width=1200,
        height=700,
        showlegend=False,
    )

    fig.show()
