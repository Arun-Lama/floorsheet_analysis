import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def plot_buyer_cumulative_turnover_from_floorsheet(combined_floorsheet, days=30):
    """
    Generate and plot the cumulative turnover for the top 10 buyers from the combined floorsheet data,
    filtered by the last `days` number of trading days.

    Parameters:
    - combined_floorsheet (DataFrame): DataFrame containing the trading data with columns 
      'Buyer', 'Amount (Rs)', and 'Date'.
    - days (int): Number of most recent trading days to include in the plot. Default is 30 days.
    """
    # Ensure 'Date' is datetime and filter data for the last `days` days
    combined_floorsheet['Date'] = pd.to_datetime(combined_floorsheet['Date'])
    cutoff_date = datetime.now() - timedelta(days=days)
    filtered_data = combined_floorsheet[combined_floorsheet['Date'] >= cutoff_date]

    # Create pivot table for buyers
    buyer_brokers = pd.pivot_table(
        filtered_data,
        values="Amount (Rs)",
        index="Buyer",
        columns="Date",
        aggfunc="sum",
        fill_value=0
    )

    # Calculate cumulative turnover for each buyer across all dates
    buyer_brokers_cumulative = buyer_brokers.cumsum(axis=1)

    # Add a "Total" column to sum the cumulative turnover for each broker
    buyer_brokers_cumulative["Total"] = buyer_brokers_cumulative.sum(axis=1)
    buyer_brokers_cumulative = buyer_brokers_cumulative.sort_values(by="Total", ascending=False)

    # Select the top 10 buyers based on the total cumulative turnover
    buyer_brokers_cumulative = buyer_brokers_cumulative.nlargest(10, "Total")

    # Plotting
    fig = make_subplots(rows=1, cols=1)

    # Plot Buyers
    for broker in buyer_brokers_cumulative.index:
        series = buyer_brokers_cumulative.loc[broker]
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines+markers',
            name=f"Buyer {broker}",
            line=dict(width=2),
            marker=dict(size=4)
        ), row=1, col=1)

    # Update layout and axis scaling
    fig.update_layout(
        title=f"Cumulative Turnover for Top 10 Buyers (Last {days} Days)",
        height=600,
        width=1000,
        xaxis_title="Date",
        yaxis_title="Cumulative Turnover (Rs)",
        yaxis=dict(type='log'),  # Use logarithmic scale for better visualization
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=100, b=100)
    )

    # Show the plot
    fig.show()

# Example usage:
# Assuming you have the combined_floorsheet DataFrame available:
# plot_buyer_cumulative_turnover_from_floorsheet(combined_floorsheet, days=30)
