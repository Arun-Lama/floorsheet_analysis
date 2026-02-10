import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

def brokers_top_accumulation(df, broker, days=30):
    """
    Generates an interactive Plotly line chart for the top 10 buyers and top 10 sellers of a given broker over time.

    Parameters:
    df (pd.DataFrame): The floorsheet data containing 'Contract No.', 'Stock Symbol', 'Buyer', 'Seller', and 'Amount (Rs)'.
    broker (str): The broker to filter the data.
    days (int): The number of days to consider for filtering the data.

    Returns:
    None: Displays the Plotly charts.
    """

    # Filter the data for the given broker
    df_filtered_buy = df[df["Buyer"] == broker].copy()
    df_filtered_sell = df[df["Seller"] == broker].copy()

    if df_filtered_buy.empty and df_filtered_sell.empty:
        print(f"No data found for broker: {broker}")
        return None

    # Convert 'Contract No.' to string and extract Date
    df_filtered_buy["Contract No."] = df_filtered_buy["Contract No."].astype(str)
    df_filtered_sell["Contract No."] = df_filtered_sell["Contract No."].astype(str)

    df_filtered_buy["Date"] = pd.to_datetime(df_filtered_buy["Contract No."].str[:8], format='%Y%m%d', errors='coerce')
    df_filtered_sell["Date"] = pd.to_datetime(df_filtered_sell["Contract No."].str[:8], format='%Y%m%d', errors='coerce')

    # Get the current date and calculate the cutoff date (last n days)
    current_date = datetime.now()
    cutoff_date = current_date - timedelta(days=days)

    # Filter the data for the last 'n' days
    df_filtered_buy = df_filtered_buy[df_filtered_buy["Date"] >= cutoff_date]
    df_filtered_sell = df_filtered_sell[df_filtered_sell["Date"] >= cutoff_date]

    if df_filtered_buy.empty and df_filtered_sell.empty:
        print(f"No recent data in the last {days} days for broker: {broker}")
        return None

    # Create pivot tables for buys and sells
    pivot_table_buy = pd.pivot_table(
        df_filtered_buy,
        values="Amount (Rs)",
        index="Stock Symbol",
        columns="Date",
        aggfunc="sum",
        fill_value=0
    )

    pivot_table_sell = pd.pivot_table(
        df_filtered_sell,
        values="Amount (Rs)",
        index="Date",
        columns="Stock Symbol",
        aggfunc="sum",
        fill_value=0
    ).T  # Transpose sell table to match buy table format (Stock Symbol x Date)

    # Compute net accumulation (buy - sell)
    pivot_table_diff = pivot_table_buy.subtract(pivot_table_sell, fill_value=0)
    pivot_table_diff["Total"] = pivot_table_diff.sum(axis=1)
    pivot_table_diff.sort_values(by="Total", ascending=False, inplace=True)

    # Top 10 buyers and top 10 sellers
    top_10_buyers = pivot_table_diff.nlargest(10, "Total")
    top_10_sellers = pivot_table_diff.nsmallest(10, "Total")

    # Plot function
    for df_subset, title in [(top_10_buyers, "Top 10 Purchase"), (top_10_sellers, "Top 10 Sales")]:
        df_no_total = df_subset.drop(columns=["Total"])
        df_cumulative = df_no_total.cumsum(axis=1)

        df_transposed = df_cumulative.T.reset_index().rename(columns={"index": "Date"})
        df_long = df_transposed.melt(id_vars='Date', var_name='Stock Symbol', value_name='Value')

        fig = go.Figure()

        for symbol in df_long["Stock Symbol"].unique():
            symbol_data = df_long[df_long["Stock Symbol"] == symbol]
            fig.add_trace(go.Scatter(
                x=symbol_data["Date"],
                y=symbol_data["Value"],
                mode='lines+markers',
                name=symbol
            ))

        fig.update_layout(
            title=f"{title} of {broker} Over Time (Last {days} Days)",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Cumulative Amount (Rs)"),
            width=900,
            height=500,
            legend=dict(orientation="h", x=0.5, y=1.1, xanchor="center")
        )

        fig.show()
