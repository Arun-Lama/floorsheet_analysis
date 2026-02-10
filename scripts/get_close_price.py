import pandas as pd 

def get_close_prices(ticker: str, date_series: pd.Series, price_history: pd.DataFrame) -> pd.DataFrame:
    """
    Get Close prices for a specific stock ticker on given dates from price_history DataFrame.
    
    Parameters:
    - ticker: string, the stock ticker symbol (e.g., 'AAPL')
    - date_series: pandas Series containing dates to look up
    - price_history: DataFrame containing historical prices with columns: ['Ticker', 'Date', 'Close']
    
    Returns:
    - pandas DataFrame with columns: ['Date', 'Close'] containing prices for the specified ticker
    - Missing dates will have NaN in the Close column
    """
    
    # Filter price_history for the specific ticker
    stock_prices = price_history[price_history['Ticker'] == ticker].copy()

    if stock_prices.empty:
        raise ValueError(f"No price history found for ticker: {ticker}")
    
    # Create a DataFrame from the date_series for merging
    query_df = pd.DataFrame({'Date': date_series})
    
    # Merge with the stock's prices (keeping all dates from query_df)
    result_df = query_df.merge(
        stock_prices[['Date', 'Close']],
        on='Date',
        how='left'
    )
    result_df['Close'] = result_df['Close'].ffill()

    # Add ticker column to identify the stock
    result_df['Ticker'] = ticker
    
    return result_df[['Date', 'Close']]  # Reorder columns for better readability