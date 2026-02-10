import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_index_history(ticker: str, date_series: pd.Series, index_history: pd.DataFrame) -> pd.DataFrame:
    index = index_history[index_history['Ticker'] == ticker].copy()
    index.reset_index(inplace=True)
    index['Date'] = pd.to_datetime(index['Date'], format="%Y-%m-%d")
    if index.empty:
        raise ValueError(f"No price history found for ticker: {ticker}")

    query_df = pd.DataFrame({'Date': date_series})
    result_df = query_df.merge(
        index[['Date', 'Close']],
        on='Date',
        how='left'
    )
    result_df['Close'] = result_df['Close'].astype(float)
    result_df['Close'] = result_df['Close'].ffill()
    return result_df


def plot_cumulative_pct_change_by_trading_days(all_stock_data, indices_data, trading_days=5, top_n=20):
    """
    Plot cumulative turnover for top `n` tickers over the last `trading_days` trading days.

    Parameters:
    - all_stock_data (DataFrame): DataFrame with 'Date', 'Ticker', 'Turnover'.
    - indices_data (DataFrame): Index data including 'Date', 'Ticker', 'Close'.
    - trading_days (int): Number of most recent trading days to include.
    - top_n (int): Number of top tickers to display.
    """

    # Ensure 'Date' is datetime and sort
    all_stock_data['Date'] = pd.to_datetime(all_stock_data['Date'])
    all_stock_data = all_stock_data.sort_values('Date')

    # Pivot and slice last N trading days
    pivot_table_buy = pd.pivot_table(
        all_stock_data,
        values="Turnover",
        index="Date",
        columns="Ticker",
        fill_value=0
    )

    pivot_table_buy = pivot_table_buy.tail(trading_days)

    # Calculate cumulative turnover
    cumulative_turnover = pivot_table_buy.cumsum()

    # Get top tickers based on latest cumulative turnover
    latest_row = cumulative_turnover.iloc[-1]
    top_tickers = latest_row.sort_values(ascending=False).head(top_n)
    time_series_top = cumulative_turnover[top_tickers.index]

    # Get index data for plotting
    index_data = get_index_history('Nepse Index', time_series_top.index, indices_data)

    # Plotting
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Plot index closing price ONCE on secondary axis
    fig.add_trace(go.Scatter(
        x=index_data['Date'],
        y=index_data['Close'],
        mode='lines',
        name='Index Closing Price',
        line=dict(color='blue', width=4),
        opacity=0.2,
    ), secondary_y=True)

    # Plot each top ticker’s cumulative turnover
    for ticker in time_series_top.columns:
        fig.add_trace(go.Scatter(
            x=time_series_top.index,
            y=time_series_top[ticker],
            mode='lines+markers',
            name=ticker,
        ), secondary_y=False)

        # Add annotation per ticker
        fig.add_annotation(
            x=time_series_top.index[-1] + pd.Timedelta(days=1),
            y=time_series_top[ticker].iloc[-1],
            text=ticker,
            showarrow=False,
            font=dict(size=10),
            xanchor='left',
            yanchor='middle',
        )

    # Final layout
    fig.update_layout(
        title=f"Cumulative Turnover for Top {top_n} Stocks Over Last {trading_days} Trading Days",
        xaxis_title="Date",
        yaxis_title="Cumulative Turnover",
        yaxis2_title="Nepse Index",
        width=1200,
        height=700,
        showlegend = False
    )

    fig.show()
