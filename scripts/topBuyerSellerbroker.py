import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta

def plot_stock_brokers(floorsheet_data, days=7):
    """
    Plot top buying and selling brokers for a stock based on recent 'days' worth of data.

    Parameters:
    - floorsheet_data (DataFrame): Must include 'Date', 'Buyer', 'Seller', 'Amount (Rs)'.
    - days (int): Number of most recent days to include in the analysis.
    """

    # Ensure Date column is datetime
    floorsheet_data['Date'] = pd.to_datetime(floorsheet_data['Date'])

    # Filter for the last 'n' days
    cutoff_date = floorsheet_data['Date'].max() - timedelta(days=days)
    filtered_data = floorsheet_data[floorsheet_data['Date'] >= cutoff_date]

    # Total transaction amount
    total_transaction_amount = filtered_data["Amount (Rs)"].sum()

    # Top 10 Buyers
    top_buyer_broker = (
        filtered_data.groupby(["Buyer"], as_index=False)["Amount (Rs)"]
        .sum()
        .sort_values(by="Amount (Rs)", ascending=False)
        .head(10)
    )
    top_buyer_broker["% of Total"] = (top_buyer_broker["Amount (Rs)"] / total_transaction_amount) * 100
    top_buyer_broker = top_buyer_broker.sort_values(by="Amount (Rs)", ascending=True)

    # Top 10 Sellers
    top_seller_broker = (
        filtered_data.groupby(["Seller"], as_index=False)["Amount (Rs)"]
        .sum()
        .sort_values(by="Amount (Rs)", ascending=False)
        .head(10)
    )
    top_seller_broker["% of Total"] = (top_seller_broker["Amount (Rs)"] / total_transaction_amount) * 100
    top_seller_broker = top_seller_broker.sort_values(by="Amount (Rs)", ascending=True)

    # Plot
    fig = make_subplots(
        rows=1, cols=2, horizontal_spacing=0.15,
        subplot_titles=(f"Top Buyers (Last {days} Days)", f"Top Sellers (Last {days} Days)")
    )

    fig.add_trace(go.Bar(
        x=top_buyer_broker["Amount (Rs)"],
        y=top_buyer_broker["Buyer"].astype(str),
        orientation="h",
        marker=dict(color="cyan"),
        text=top_buyer_broker.apply(lambda row: f"{row['Amount (Rs)']:,.0f} ({row['% of Total']:.2f}%)", axis=1),
        textposition="inside"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=top_seller_broker["Amount (Rs)"],
        y=top_seller_broker["Seller"].astype(str),
        orientation="h",
        marker=dict(color="gold"),
        text=top_seller_broker.apply(lambda row: f"{row['Amount (Rs)']:,.0f} ({row['% of Total']:.2f}%)", axis=1),
        textposition="inside"
    ), row=1, col=2)

    fig.update_layout(
        title_text=f"Top Brokers for Last {days} Days",
        template="plotly_white",
        width=1000, height=600,
        showlegend=False
    )
    fig.update_xaxes(tickformat=",", title_text="Amount (Rs)", row=1, col=1)
    fig.update_xaxes(tickformat=",", title_text="Amount (Rs)", row=1, col=2)

    fig.show()
