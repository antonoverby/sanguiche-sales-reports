import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(layout='wide', initial_sidebar_state="expanded", page_title="Sanguiche Sales Reports")
st.title("Sanguiche Sales Reports")
st.markdown("#### Choose a reporting date range below and use the sidebar to choose which graphs to see")
st.sidebar.subheader("Pick which graphs to see")

# LOAD AND TRANSFORM DATA SECTION ############################## 
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
    # Take out "Custom Amount" category of items
    sales = sales[sales['Item'].str.contains("Custom Amount") == False]
    # Gross Sales to float
    sales['Gross Sales'] = sales['Gross Sales'].str.replace('$','').astype(float)

    return sales

sales = load_sales_data()
##################################################################

# DATE RANGE PICKER SECTION ######################################
start_date = datetime(2023, 6, 1)
end_date = datetime.now()
with st.expander("**Report Date Range**"):
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader("Report Date Range")
        date_input = st.date_input("(Double click a date to see one day)", value=(start_date, end_date))
        if len(date_input) != 2:
            st.stop()
start_input = date_input[0]
end_input = date_input[1]
    
# Define sales DF as between the date ranges selected
sales = sales.loc[sales['Date'].between(start_input, end_input)]
##################################################################

# TOTAL SALES BY DAY SECTION #####################################
def sales_bar_graph(df, roll_avg_win: int):
    _ = df.groupby('Date')['Gross Sales'].agg(list).to_dict()
    sales_by_day_dict = {k:sum(v) for k, v in _.items()}
    sales_df = pd.DataFrame.from_dict(list(sales_by_day_dict.items()))
    sales_df.columns = ['Date', 'SumTot']
    sales_df['MovAvg'] = sales_df['SumTot'].rolling(roll_avg_win, min_periods=1).mean()
    fig = px.bar(df, x=[day.strftime("%Y/%m/%d")for day in sales_df['Date']], y=sales_df['SumTot'], text=sales_df['SumTot'],
                  labels={
                      "x":"Date",
                      "y":"Sales"
                  },
                  title='Sales by Day')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    fig.add_traces(
        px.scatter(sales_df, x=[day.strftime("%Y/%m/%d")for day in sales_df['Date']], y=sales_df['MovAvg']).update_traces(mode='lines+markers', line=dict(color='red'), marker=dict(color='red')).data
                  )
    max_dict_value = max(sales_by_day_dict.values())
    fig.update_xaxes(dtick="D1",
                     tickformatstops=[
        dict(dtickrange=[None, 86400000], value="%a %b %d %Y")
    ]
    )
    fig.update_yaxes(range=(0, max_dict_value + 100))
    
    return st.plotly_chart(fig, use_container_width=True)

sales_tot_graph = st.sidebar.checkbox(label='Sales Totals by Day')
if sales_tot_graph:
    st.subheader(f"Total sales for {date_input[0].strftime('%m/%d/%Y')} to {date_input[1].strftime('%m/%d/%Y')}", help="*doesn't include Custom Amount items")
    st.write("*rolling average line in red")

    try:    
        sales_bar_graph(sales, roll_avg_win=4)
    except ValueError as e:
        st.subheader("This date has no data. Please select a date or date range where sales occurred.")
        st.write(e)
        st.stop()

##################################################################

# DAY OF WEEK AVG SALES ##########################################
def dow_avg_sales_bar(df):
    _ = df.groupby('Date')['Gross Sales'].agg(list).to_dict()
    sales_by_day_dict = {k:sum(v) for k, v in _.items()}
    sales_df = pd.DataFrame.from_dict(list(sales_by_day_dict.items()))
    sales_df.columns = ['Date', 'SalesAvg']
    sales_df['Date'] = pd.to_datetime(sales_df['Date'])
    sales_df['DayofWeek'] = sales_df['Date'].dt.day_name()
    dow_avg = round(sales_df.groupby('DayofWeek')['SalesAvg'].mean(), 2)
    dow_avg = pd.Series.to_frame(dow_avg)

    fig = px.bar(dow_avg, x=dow_avg.index, y='SalesAvg')
    fig.update_xaxes(categoryorder='array', categoryarray=['Thursday', 'Friday', 'Saturday', 'Sunday', 'Monday'])
    fig.update_traces(texttemplate='%{y}', textposition='outside')

    return st.plotly_chart(fig, use_container_width=True)

dow_avg_graph = st.sidebar.checkbox(label='Sales Avg - Day of the Week')
if dow_avg_graph:
    st.subheader(f"Average Sales Totals by Day of the Week for {date_input[0].strftime('%m/%d/%Y')} to {date_input[1].strftime('%m/%d/%Y')}")
    st.write("**Note**: Choosing one week as date range will show total sales figures, not an average")
    
    try:    
        dow_avg_sales_bar(sales)
    except ValueError as e:
        st.subheader("This date has no data. Please select a date or date range where sales occurred.")
        st.write(e)
        st.stop()

##################################################################

# SALES BY HOUR OF DAY ###########################################
def tod_sales_bar(df):
    _ = sales.groupby('Time')['Qty'].agg(list).to_dict()
    sales_by_day_dict = {k:sum(v) for k, v in _.items()}
    sales_df = pd.DataFrame.from_dict(list(sales_by_day_dict.items()))
    sales_df.columns = ['Time', 'Sales']
    sales_df['Time'] = pd.to_datetime(sales_df['Time'])
    sales_df['Hour'] = sales_df['Time'].dt.hour
    tod_avg = sales_df.groupby('Hour')['Sales'].sum()
    tod_avg = pd.Series.to_frame(tod_avg)

    fig = px.bar(tod_avg, x=tod_avg.index, y='Sales')
    fig.update_xaxes(tickmode='linear')    
    fig.update_traces(texttemplate='%{y}', textposition='outside')

    return st.plotly_chart(fig, use_container_width=True)

tod_avg_graph = st.sidebar.checkbox(label='Sales - Hour of the Day')
if tod_avg_graph:
    st.subheader(f"Total Sales by Hour of the Day for {date_input[0].strftime('%m/%d/%Y')} to {date_input[1].strftime('%m/%d/%Y')}")
    
    try:    
        tod_sales_bar(sales)
    except ValueError as e:
        st.subheader("This date has no data. Please select a date or date range where sales occurred.")
        st.write(e)
        st.stop()
##################################################################

# SALES BY ITEM OVER TIME ########################################
def cum_item_sales_line(df, y_buffer: int, category="Sandwiches" or "Sides" or "Add Ons"):
    item_by_day = df.groupby(['Date', 'Item', 'Category'], as_index=False)['Qty'].sum()
    item_by_day['CumSum'] = item_by_day.groupby('Item')['Qty'].cumsum()
    item_by_day = item_by_day[item_by_day['Category'] == category]
    fig = px.line(item_by_day, x='Date', y='CumSum', color='Item', 
                  labels={
                      'x':'Date',
                      'y':'CumSum'
                  })
    fig.update_traces(mode='lines+markers')
    max_value = item_by_day['CumSum'].max()
    fig.update_yaxes(range=(0, max_value + y_buffer))
    
    return st.plotly_chart(fig, use_container_width=True)

item_time_graph = st.sidebar.checkbox(label='Item Sales Over Time')
if item_time_graph:
    st.subheader(f"Cumulative Sales by Item for {date_input[0].strftime('%m/%d/%Y')} to {date_input[1].strftime('%m/%d/%Y')}")
    
    st.subheader("Sandwiches")
    cum_item_sales_line(sales,category="Sandwiches", y_buffer=5)
    st.subheader('Sides')
    cum_item_sales_line(sales, category="Sides", y_buffer=5)
    st.subheader('Add Ons')
    cum_item_sales_line(sales, category="Add Ons", y_buffer=2)

# ##################################################################

# SALES BY ITEM CATEGORY SECTION #################################
def sales_by_item_barchart(df, y_buffer: int):
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
    fig.update_yaxes(range=(0, max_dict_value + y_buffer))
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

item_tot_graph = st.sidebar.checkbox(label='Item Sales Totals')
if item_tot_graph:
    st.subheader(f"Total Sales by Item for {date_input[0].strftime('%m/%d/%Y')} to {date_input[1].strftime('%m/%d/%Y')}")
    
    st.subheader(f"# Sandwiches Sold: {int(num_sandwiches)}")
    try:
        sales_by_item_barchart(sandwich_sales, y_buffer=30)
    except ValueError as e:
        st.write("There's no data to display")
    
    st.subheader(f"# Sides Sold: {int(num_sides)}")
    try:
        sales_by_item_barchart(sides, y_buffer=30)
    except ValueError as e:
        st.write("There's no data to display")

    st.subheader(f"# Add-ons Sold: {int(num_addon)}")
    try:
        sales_by_item_barchart(addon_sales, y_buffer=5)
    except ValueError as e:
        st.write("There's no data to display")
##################################################################

# # SCHEDULING DATA INPUT ##########################################
# def sched_input_table():
#     df = pd.DataFrame(columns=['Date', 'Employee'])
#     df = st.data_editor(df, use_container_width=True, num_rows='dynamic',
#                         column_config={
#                             'Date': st.column_config.DateColumn(),
#                             'Employee': st.column_config.SelectboxColumn(options=['Alex', 'Anton', 'Mike', 'Randal', 'Sam'])
#                         })

#     return df

# @st.cache_data
# def sched_to_csv(df):
#     return df.to_csv().encode('utf-8')

# sched = sched_input_table()
# sched_csv = sched_to_csv(sched)

# st.download_button(
#     label='Download Schedule to CSV',
#     data=sched_csv,
#     file_name='sched.csv',
#     mime='text/csv'
#     )

# ##################################################################