import pandas as pd
import streamlit as st
import plotly.express as px
st.set_page_config(layout='wide', initial_sidebar_state="collapsed")
sales = pd.read_csv("data\sales-6.5.23-to-6.11.23.csv")

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



