import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(layout='wide', initial_sidebar_state="collapsed", page_title="Sanguiche Sales Reports")
st.title("Sanguiche Sales Reports")

def load_sales_data():
    sales = pd.read_csv("data/sales.csv")
    # Date to datetimeobject
    sales['Date'] = pd.to_datetime(sales['Date']).dt.date
    # Replace old item and category names with current ones
    item_name_replacement = {"(ZM) Meatball Parm": "Meatball sub", "(ZM) Chicken Parm": "Chicken Parm", "Meatball Sub (ZM)": "Meatball sub", "Eggplant Parm (ZM)": "Eggplant Parm", "Cassie (ZM)": "Cassie", "Cold Cut Combo(ZM)":"Cold Cut Combo", "Chicken Parm (ZM)": "Chicken Parm", "The Caprese": "Caprese", "Cold Cut": "Cold Cut Combo", "Zapps (ZM)": "Zapps", "Mozz Stix (ZM)":"Mozz Stix", "(ZM)Mozz Stix": "Mozz Stix", "Garlic Bread (ZM)":"Garlic Bread", "Zappa (ZM)": "Zapps", "Chicken Parmesan Sandwich": "Chicken Parm", "Eggplant Parmesan Sandwich": "Eggplant Parm", "Meatball Sub Sandwich": "Meatball sub"}
    for k, v in item_name_replacement.items():
        sales.replace(k, v, inplace=True)
    cat_name_replacement = {"Finger Food": "Sides"}
    for k, v in cat_name_replacement.items():
        sales.replace(k, v, inplace=True)
    # Replace where Category is NaN with the correct type of category
    sandwiches = ['Meatball sub', 'Eggplant Parm', 'Cold Cut Combo', 'Chicken Parm', 'Caprese', 'Cassie', 'Sausage']
    sides = ['Single Meatball', 'Mozz Stix', 'Meatball Slider', 'Eggplant Fries', 'Garlic Bread', 'Zapps']
    sales['Category'] = np.where((sales['Category'].isnull()) & (sales['Item'].isin(sandwiches)), 'Sandwiches', sales['Category'])
    sales['Category'] = np.where((sales['Category'].isnull()) & (sales['Item'].isin(sides)), 'Sides', sales['Category'])

    return sales

sales = load_sales_data()

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

def sales_line_graph(df):
    sales['Gross Sales'] = sales['Gross Sales'].str.replace('$','').astype(float)
    _ = df.groupby('Date')['Gross Sales'].agg(list).to_dict()
    sales_by_day_dict = {k:sum(v) for k, v in _.items()}
    days = list(sales_by_day_dict.keys())
    sales_totals = list(sales_by_day_dict.values())
    fig = px.line(df, x=days, y=sales_totals)

    return st.plotly_chart(fig, use_container_width=True)

sales_line_graph(sales)

def sales_by_item_barchart(df):
    # make items and total sales dictionary
    _ = df.groupby('Item')['Qty'].agg(list).to_dict()
    item_sales_dict = {k:sum(v) for k, v in _.items()}
    item_key = list(item_sales_dict.keys())
    tot_sales_values = list(item_sales_dict.values())
    max_dict_value = max(item_sales_dict.values()) 
    fig = px.bar(sales, x=item_key, y=tot_sales_values, 
                 labels ={
                     "x": "Items",
                     "y": "Number Sold"
                 })
    fig.update_xaxes(categoryorder='total descending')
    fig.update_yaxes(range=(0, max_dict_value + 5))
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return st.plotly_chart(fig, use_container_width=True)


# Define different category DFs
sandwich_sales = sales[sales['Category'] == 'Sandwiches']
sides = sales[sales['Category'] == 'Sides']
addon_sales = sales[sales['Category'] == 'Add Ons']

# Define quantity totals
num_sandwiches = sandwich_sales['Qty'].sum()
num_sides = sides['Qty'].sum()
num_addon = addon_sales['Qty'].sum()

# Streamlit structure
st.header(f"Sales by item for {date_input[0]} to {date_input[1]}")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader(f"# Sandwiches Sold: {int(num_sandwiches)}")
    sales_by_item_barchart(sandwich_sales)
with col2:
    st.subheader(f"# Sides Sold: {int(num_sides)}")
    sales_by_item_barchart(sides)
with col3:
    st.subheader(f"# Add-ons Sold: {int(num_addon)}")
    sales_by_item_barchart(addon_sales)
