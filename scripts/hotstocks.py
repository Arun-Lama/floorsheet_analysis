import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def hot_stocks_custom(data):
    while True:
        try:
            num_of_bars = int(input("Enter a number between 1 and 5 to define the bar grouping: "))
            if 1 <= num_of_bars <= 5:
                break
            else:
                print("Please enter a valid number between 1 and 5.")
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 5.")

    num_of_periods = 50  # 50 periods of the selected bar grouping

    # Pivot volume table
    pivot_volume = pd.pivot_table(data, values='Volume', index=['Date'], columns=['Ticker']).fillna(0)
    latest_trading_day = pivot_volume.index[-1]
    # Aggregate bars using rolling sum instead of resampling by calendar days
    grouped_volume = pivot_volume.rolling(num_of_bars).sum()

    # Compute rolling average over 50 periods of the selected grouping
    rolling_avg_volume = grouped_volume.rolling(num_of_periods).mean()

    # Calculate percentage difference from 50-bar average for the selected bar size
    vol_vs_avgVol = ((grouped_volume / rolling_avg_volume) - 1) * 100
    vol_vs_avgVol = vol_vs_avgVol[-1:].fillna(0)
    vol_vs_avgVol.reset_index(drop=True, inplace=True)
    vol_vs_avgVol = vol_vs_avgVol.transpose()
    vol_vs_avgVol.rename(columns={vol_vs_avgVol.columns[0]: f"Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol"}, inplace=True)

    # Sort and select top 40 stocks with highest volume surge
    vol_vs_avgVol = vol_vs_avgVol.sort_values([f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol'], ascending=False).nlargest(40, [f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol'])
    vol_vs_avgVol = vol_vs_avgVol.sort_values([f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol'], ascending=False).round(2)

    # Split into two equal parts
    vol_vs_avgVol_split = np.array_split(vol_vs_avgVol, 2)
    vol_vs_avgVol_split_first_part = vol_vs_avgVol_split[0].sort_values([f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol'], ascending=True)

    # Plot first part of hot stocks
    fig, ax1 = plt.subplots(figsize=(8, 6))
    plt.rcParams['figure.facecolor'] = 'white'
    ax1.barh(vol_vs_avgVol_split_first_part.index, vol_vs_avgVol_split_first_part[f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol'], color='dodgerblue')
    ax1.set_title(f"Hot Stocks as on {latest_trading_day.date()} (Current {num_of_bars}-Bar Vol / Avg {num_of_periods} {num_of_bars}-Bar Vol) %", fontsize=12)
    ax1.axes.get_xaxis().set_visible(False)
    ax1.set_facecolor('xkcd:white')

    # Remove unnecessary spines
    for spine in ['right', 'top', 'left', 'bottom']:
        ax1.spines[spine].set_visible(False)

    # Add labels to bars
    for index, value in enumerate(vol_vs_avgVol_split_first_part[f'Last {num_of_bars}-Bar Vol Vs Avg {num_of_periods} {num_of_bars}-Bar Vol']): 
        ax1.text(value, index, f"{value:.2f}%", va='center', fontsize=10, color='black')

    plt.tight_layout()
    plt.show()
