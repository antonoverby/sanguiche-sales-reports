import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

st.set_page_config(layout='wide', initial_sidebar_state="collapsed")

sales = pd.read_csv("data/sales-6.5.23-to-6.11.23.csv")
sales['Date'] = pd.to_datetime(sales['Date']).dt.date

# Date range picker
start_date = datetime(2023, 6, 1)
end_date = datetime.now()
date_input = st.date_input("Select a date range", value=(start_date, end_date))
if len(date_input) != 2:
    st.stop()
start_input = date_input[0]
end_input = date_input[1]
    
# Define sales DF as between the date ranges selected
sales = sales.loc[sales['Date'].between(start_input, end_input)]
sandwich_sales = sales[sales['Category'] == 'Sandwiches']
sides = sales[sales['Category'] == 'Sides']
addon_sales = sales[sales['Category'] == 'Add Ons']

def sales_by_item_barchart(df):
    # make items and total sales dictionary
    _ = df.groupby('Item')['Qty'].agg(list).to_dict()
    item_sales_dict = {k:sum(v) for k, v in _.items()}
    item_key = list(item_sales_dict.keys())
    tot_sales_values = list(item_sales_dict.values()) 
    fig = px.bar(sales, x=item_key, y=tot_sales_values)
    fig.update_xaxes(categoryorder='total descending')
    fig.update_traces(textposition='outside')
    return st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Sandwich sales totals")
    sales_by_item_barchart(sandwich_sales)
with col2:
    st.subheader("Sides sales totals")
    sales_by_item_barchart(sides)
with col3:
    st.subheader("Add-on sales totals")
    sales_by_item_barchart(addon_sales)
