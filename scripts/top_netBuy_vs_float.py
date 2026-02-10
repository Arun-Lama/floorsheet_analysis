import plotly.express as px


def top_NetBuyVsFloat(combined_floorsheet, float_data, active_comps, n_day, top_n):
    floor_sheet_reduced = combined_floorsheet[['Stock Symbol', 'Buyer', 'Seller', 'Quantity', 'Date']]
    filtered_df = floor_sheet_reduced[floor_sheet_reduced['Stock Symbol'].isin(active_comps['Symbol'])]
    nth_date = filtered_df['Date'].drop_duplicates().sort_values().iloc[-(n_day + 1)]
    n_day_floorsheet = filtered_df[filtered_df['Date'] >= nth_date]
    pivot_df_buy = n_day_floorsheet.pivot_table(
        index='Stock Symbol',
        columns='Buyer',
        values='Quantity',
        aggfunc='sum',
        fill_value=0
    )

    pivot_df_sell = n_day_floorsheet.pivot_table(
    index='Stock Symbol',
    columns='Seller',
    values='Quantity',
    aggfunc='sum',
    fill_value=0
)
    pivot_table_diff = pivot_df_buy.sub(pivot_df_sell, fill_value=0)
    float_shares = float_data[['Symbol', 'Floated Shares']]
    float_shares.set_index('Symbol', inplace = True)
    
    # Make sure 'Floated Shares' is aligned to pivot_df's index
    float_percent = pivot_table_diff.div(float_shares['Floated Shares'], axis=0)
    
    unstacked = float_percent.unstack()
    
    top_n = unstacked.nlargest(top_n)
    
    top_n_df =  top_n.reset_index()
    top_n_df.columns = ['Buyer Broker', 'Company', 'Net Buy/float (%)']


    # Combine 'Buyer Broker' and 'Company' into a single label
    top_n_df['Label'] = top_n_df['Buyer Broker'].astype(str) + ' - ' + top_n_df['Company']

    # Sort for cleaner layout (optional)
    top_n_df = top_n_df.sort_values('Net Buy/float (%)', ascending=True)

    # Dynamically set height: 25 pixels per row, with a minimum of 250 and max of 1000 (optional caps)
    row_height = 25
    min_height = 250
    max_height = 1000
    calculated_height = min(max(len(top_n_df) * row_height, min_height), max_height)

    # Create horizontal bar chart
    fig = px.bar(
        top_n_df,
        x='Net Buy/float (%)',
        y='Label',
        orientation='h',
        text='Net Buy/float (%)',
        labels={'Label': 'Buyer Broker - Company', 'Net Buy/float (%)': 'Net Buy/Float (%)'},
    )

    # Customize layout
    fig.update_traces(
        texttemplate='%{text:.2%}',
        textposition='outside',
        marker_color='teal',
    )

    fig.update_layout(
        height=calculated_height,
        margin=dict(l=60, r=20, t=40, b=20),
        yaxis=dict(tickfont=dict(size=10)),
        xaxis_tickformat=".2%",
        showlegend=False,
        title='Net Buy/Float (%) by Buyer Broker and Company',
    )

    fig.show()



    