import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
from get_close_price import get_close_prices
import os
import plotly.express as px

def plot_top_buyers_sellers(
    df, price_history, stock, file_index,
    output_folder=None, days=30, save=False, show=True
    ):
    """
    Plots top net buyers' cumulative positions with scaled VPT and closing price.
    """
    top_n = 500
    def filter_recent_trades(df, stock, days):
        df_stock = df[df["Stock Symbol"] == stock].copy()
        if df_stock.empty:
            print(f"No data for stock: {stock}")
            return None, None
        unique_dates = df_stock['Date'].drop_duplicates().sort_values()
        if len(unique_dates) < days:
            print(f"Not enough trading days: Requested {days}, Got {len(unique_dates)}")
            return None, None
        cutoff = unique_dates.iloc[-days]
        return df_stock[df_stock["Date"] >= cutoff], unique_dates[unique_dates >= cutoff]

    def compute_top_cumulative(df_filtered, full_date_range, top_n):
        buy = df_filtered.groupby(["Buyer", "Date"])["Amount (Rs)"].sum().unstack(fill_value=0)
        sell = df_filtered.groupby(["Seller", "Date"])["Amount (Rs)"].sum().unstack(fill_value=0)
        all_dates = sorted(set(buy.columns).union(set(sell.columns)))
        buy, sell = buy.reindex(columns=all_dates, fill_value=0), sell.reindex(columns=all_dates, fill_value=0)
        net = buy.subtract(sell, fill_value=0)
        net["Total"] = net.sum(axis=1)
        top = net["Total"].nlargest(top_n).index
        net_top = net.loc[top].drop(columns="Total").reindex(columns=full_date_range, fill_value=0)
        return net_top.cumsum(axis=1)

    def compute_scaled_vpt(price_df, date_range):
        df = price_df[(price_df['Ticker'] == stock)].copy()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'].isin(date_range)].sort_values("Date")
        df['DailyReturn'] = df['Close'].pct_change().fillna(0)
        df['VPT'] = (df['Turnover'] * df['DailyReturn']).cumsum().fillna(0)
        # Scale to closing price range
        vpt = df['VPT']
        close = df['Close']
        df['VPT_Scaled'] = ((vpt - vpt.min()) / (vpt.max() - vpt.min())) * (close.max() - close.min()) + close.min()
        return df[["Date", "Close", "VPT_Scaled"]].copy()

    # --- Begin processing ---
    df_filtered, date_range = filter_recent_trades(df, stock, days)
    if df_filtered is None:
        return None

    price_data = get_close_prices(stock, date_range, price_history).dropna().sort_values("Date")
    full_dates = price_data["Date"].unique()

    cumulative_df = compute_top_cumulative(df_filtered, full_dates, top_n)
    vpt_df = compute_scaled_vpt(price_history, full_dates)

    # Melt for plot
    df_long = cumulative_df.T.reset_index().melt(id_vars="Date", var_name="Trader", value_name="Cumulative Amount (Rs)")

    # --- Plotting ---
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, specs=[[{"secondary_y": True}]])

    # Traders' net buys
    for trader in df_long["Trader"].unique():
        tdf = df_long[df_long["Trader"] == trader]
        fig.add_trace(go.Scatter(
            x=tdf["Date"], y=tdf["Cumulative Amount (Rs)"], mode='lines+markers',
            name=trader, line=dict(width=1), showlegend=False
        ), secondary_y=False)
        # Add trader label at last point
        fig.add_trace(go.Scatter(
            x=[tdf["Date"].iloc[-1]], y=[tdf["Cumulative Amount (Rs)"].iloc[-1]],
            text=[trader], mode="text", textposition="middle right", showlegend=False
        ), secondary_y=False)

    # Closing price
    fig.add_trace(go.Scatter(
        x=price_data["Date"], y=price_data["Close"], mode='lines',
        name="Closing Price", line=dict(color="orange", width=4), opacity=0.8
    ), secondary_y=True)

    # VPT Scaled
    fig.add_trace(go.Scatter(
        x=vpt_df["Date"], y=vpt_df["VPT_Scaled"], mode='lines',
        name="VPT (scaled)", line=dict(color="red", width=4, dash='dot'), opacity=0.9
    ), secondary_y=True)

    # --- Layout ---
    fig.update_layout(
        title=f"<b><span style='color:red'>{stock}</span></b> (Last {days} Trading Days - Net Buying)",
        height=600, width=1000,
        xaxis=dict(title='Date', type='date', tickformat='%b %d'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        showlegend=True
    )
    fig.update_yaxes(title_text="Net Buying Amount (Rs)", secondary_y=False)
    fig.update_yaxes(title_text="Price / VPT (scaled)", secondary_y=True)

    # --- Show or Save ---
    if show:
        fig.show()
    if save:
        if output_folder is None:
            raise ValueError("Output folder must be provided when save=True")
        os.makedirs(output_folder, exist_ok=True)
        fig.write_image(f"{output_folder}/{file_index}{stock}.png")



def calculate_cornering_strength(
    combined_floorsheet,
    active_comps,
    float_data,
    top_n,
    days=10
):
    """
    Calculates cornering strength for each stock based on the net buy/sell quantities 
    of the top two brokers over the past N trading days.

    Returns:
        pd.DataFrame with columns:
        Ticker, x up from 2nd Broker, Buyer Broker, Kitta, % of Float Kitta
    """

    import pandas as pd
    import plotly.express as px

    # -----------------------------
    # Group floorsheet by symbol
    # -----------------------------
    grouped_floorsheet = dict(
        tuple(combined_floorsheet.groupby("Stock Symbol"))
    )

    # Remove problematic symbols
    symbols_to_remove = {"NLO", "BNL", "BNT", "UNL"}
    for symbol in symbols_to_remove:
        grouped_floorsheet.pop(symbol, None)

    # Only non-index stocks
    tickers = active_comps.loc[
        active_comps["Sector"] != "Index", "Symbol"
    ]

    all_stock = []

    # -----------------------------
    # Main loop
    # -----------------------------
    for symbol in tickers:
        df_filtered = grouped_floorsheet.get(symbol)

        if df_filtered is None or df_filtered.empty:
            continue

        # Ensure Date is datetime
        df_filtered = df_filtered.copy()
        df_filtered["Date"] = pd.to_datetime(df_filtered["Date"])

        # Get last N trading days
        unique_dates = df_filtered["Date"].drop_duplicates().sort_values()

        if len(unique_dates) < days:
            continue

        cutoff_date = unique_dates.iloc[-days]
        df_filtered = df_filtered[df_filtered["Date"] >= cutoff_date]

        if df_filtered.empty:
            continue

        # -----------------------------
        # Buy vs Sell aggregation
        # -----------------------------
        buy_qty = (
            df_filtered
            .groupby(["Buyer", "Date"])["Amount (Rs)"]
            .sum()
            .unstack(fill_value=0)
        )

        sell_qty = (
            df_filtered
            .groupby(["Seller", "Date"])["Amount (Rs)"]
            .sum()
            .unstack(fill_value=0)
        )

        pivot_table_diff = buy_qty.sub(sell_qty, fill_value=0)
        pivot_table_diff["Total"] = pivot_table_diff.sum(axis=1)
        pivot_table_diff = pivot_table_diff.sort_values(
            by="Total", ascending=False
        )

        # Need at least 2 brokers
        if pivot_table_diff.shape[0] < 2:
            continue

        first_accumulator = pivot_table_diff.iloc[0]["Total"]
        second_accumulator = pivot_table_diff.iloc[1]["Total"]

        if pd.isna(first_accumulator) or second_accumulator == 0:
            continue

        difference_ratio = first_accumulator / second_accumulator

        all_stock.append({
            "Ticker": symbol,
            "x up from 2nd Broker": difference_ratio,
            "Buyer Broker": pivot_table_diff.index[0],
            "Kitta": first_accumulator
        })

    # -----------------------------
    # SAFETY: empty result
    # -----------------------------
    if not all_stock:
        print("No stocks qualified for cornering strength.")
        return pd.DataFrame()

    # -----------------------------
    # Build final DataFrame
    # -----------------------------
    df = (
        pd.DataFrame(all_stock)
        .sort_values("x up from 2nd Broker", ascending=False)
        .head(top_n)
    )

    # Merge float data
    df = df.merge(
        float_data[["Symbol", "Floated Shares"]],
        left_on="Ticker",
        right_on="Symbol",
        how="left"
    )

    df["% of Float Kitta"] = (
        df["Kitta"] / df["Floated Shares"] * 100
    )

    df.drop(columns=["Symbol", "Floated Shares"], inplace=True)
    df = df.round(2)

    # -----------------------------
    # Plot labels
    # -----------------------------
    df["Label"] = (
        df["Ticker"] + " (Broker " +
        df["Buyer Broker"].astype(str) + ")"
    )

    df["Custom Text"] = (
        "(" +
        df["x up from 2nd Broker"].map(lambda x: f"{x:.2f}×") +
        ", " +
        df["% of Float Kitta"].map(lambda x: f"{x:.2f}%") +
        ")"
    )

    # -----------------------------
    # Dynamic chart height
    # -----------------------------
    row_height = 25
    min_height = 250
    max_height = 1000
    height = min(max(len(df) * row_height, min_height), max_height)

    # -----------------------------
    # Plot
    # -----------------------------
    df_plot = df.sort_values("x up from 2nd Broker", ascending=True)

    fig = px.bar(
        df_plot,
        x="x up from 2nd Broker",
        y="Label",
        orientation="h",
        text="Custom Text",
        title="X Up from 2nd Broker by Ticker and Buyer Broker",
        labels={
            "x up from 2nd Broker": "X Up from 2nd Broker",
            "Label": "Ticker (Broker)"
        }
    )

    fig.update_layout(
        height=height,
        margin=dict(l=80, r=40, t=40, b=20),
        yaxis=dict(categoryorder="total ascending"),
        showlegend=False
    )

    fig.update_traces(
        textposition="outside",
        marker_color="darkcyan"
    )

    fig.show()

    return df





def plot_buyer_seller_sankey(
    df, stock, file_index=None,
    output_folder=None, days=30,
    save=False, show=True, top_n=10
):
    df_stock = df[df["Stock Symbol"] == stock].copy()
    if df_stock.empty:
        raise ValueError(f"No data found for stock: {stock}")
    
    df_stock["Date"] = pd.to_datetime(df_stock["Date"])
    unique_dates = df_stock["Date"].sort_values().unique()
    cutoff = unique_dates[0] if len(unique_dates) < days else unique_dates[-days]
    df_filtered = df_stock[df_stock["Date"] >= cutoff]

    # Compute total bought and sold
    total_bought = df_filtered.groupby("Buyer")["Amount (Rs)"].sum()
    total_sold = df_filtered.groupby("Seller")["Amount (Rs)"].sum()

    brokers = pd.concat([total_bought, total_sold], axis=1, keys=["Bought", "Sold"]).fillna(0)
    brokers["Net"] = brokers["Bought"] - brokers["Sold"]
    
    # Split into net sellers and net buyers
    net_sellers = brokers[brokers["Net"] < 0].copy()
    net_buyers = brokers[brokers["Net"] > 0].copy()

    # Keep top N by absolute net position
    top_sellers = net_sellers["Net"].abs().nlargest(top_n).index.tolist()
    top_buyers = net_buyers["Net"].nlargest(top_n).index.tolist()

    # Filter original trades for only these brokers
    flow_df = df_filtered[
        df_filtered["Seller"].isin(top_sellers) & df_filtered["Buyer"].isin(top_buyers)
    ].groupby(["Seller", "Buyer"])["Amount (Rs)"].sum().reset_index()

    if flow_df.empty:
        print("No matching flows found between top sellers and buyers.")
        return None

    # Create node list with unique sellers and buyers (no overlap)
    sellers = sorted(flow_df["Seller"].unique())
    buyers = sorted(flow_df["Buyer"].unique())
    nodes = sellers + buyers
    node_map = {name: i for i, name in enumerate(nodes)}

    # Build Sankey structure
    sources = flow_df["Seller"].map(node_map).tolist()
    targets = flow_df["Buyer"].map(node_map).tolist()
    values = flow_df["Amount (Rs)"].tolist()

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes,
            color=["#FF9999"] * len(sellers) + ["#99CCFF"] * len(buyers)
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color='rgba(160,160,160,0.4)',
            hovertemplate='<b>%{source.label}</b> → <b>%{target.label}</b><br>Shares: %{value:,}<extra></extra>'
        )
    ))

    fig.update_layout(
        title_text=f"{stock} Net Broker Flows (Last {len(df_filtered['Date'].unique())} Days)",
        font_size=12,
        width=1000,
        height=600
    )

    if save:
        os.makedirs(output_folder, exist_ok=True)
        filename = f"sankey_clean_{stock}_{file_index}.html" if file_index else f"sankey_clean_{stock}.html"
        fig.write_html(os.path.join(output_folder, filename))

    if show:
        fig.show()

