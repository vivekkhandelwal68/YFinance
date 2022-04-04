import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import calendar
from PIL import Image



def calculate_next_month_date(start_date : datetime) -> datetime:
    year =  start_date.year
    month = start_date.month
    if month == 12:
        month = 1
        year = year + 1
    else:
        month = month + 1
    first_day, last_day = calendar.monthrange(year, month)
    return datetime.date(year, month, 1), datetime.date(year, month, last_day)

def calculate_back_month_date(start_date : datetime) -> datetime:
    year =  start_date.year
    month = start_date.month
    if month == 1:
        month = 12
        year = year - 1
    else:
        month = month - 1
    first_day, last_day = calendar.monthrange(year, month)
    return datetime.date(year, month, 1), datetime.date(year, month, last_day)

def calculate_end_date():
    year =  st.session_state["start_date"].year
    month = st.session_state["start_date"].month
    first_day, last_day = calendar.monthrange(year, month)
    st.session_state["end_date"] = datetime.date(year, month, last_day)


def get_next_dates():
    new_start_date, new_end_date = calculate_next_month_date(st.session_state["start_date"])
    st.session_state["start_date"] = new_start_date
    st.session_state["end_date"] = new_end_date

def get_back_dates():
    new_start_date, new_end_date = calculate_back_month_date(st.session_state["start_date"])
    st.session_state["start_date"] = new_start_date
    st.session_state["end_date"] = new_end_date

def df_to_csv(data):
    return data.to_csv().encode('utf-8')


def final_calculation(symbol, org):
    if ("start_date" not in st.session_state) and ("end_date" not in st.session_state):
        today = datetime.date.today()
        previous_start_day, previous_end_day =  calculate_back_month_date(today)
        st.session_state["start_date"] = previous_start_day
        st.session_state["end_date"] = previous_end_day
    
   
    
    st.title(f'{org}({symbol})')
    start_date_col, end_date_col = st.columns(2)
    start_date = start_date_col.date_input("Start Date", st.session_state["start_date"], key="start_date", on_change=calculate_end_date)
    end_date = end_date_col.date_input("End Date", st.session_state["end_date"], key="end_date")
    data = yf.download(symbol, start=start_date, end=end_date)
    data = data.reset_index()
    st.markdown("")
    df_expander = st.expander(label='DataFrame')
    with df_expander:
        st.dataframe(data)
        csv = df_to_csv(data)
        st.download_button(
        label="Download CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
        )
    st.markdown("")
    # st.session_state
    next_button_col, back_button_col = st.columns(2)
    current_date = datetime.date.today()

    if start_date.year == current_date.year and start_date.month == current_date.month:
        next_button_col.button("Next", on_click=get_next_dates, disabled=True)
    else:
        next_button_col.button("Next", on_click=get_next_dates)
    back_button_col.button("Back", on_click=get_back_dates)

    data.set_index("Date", inplace=True)

    st.line_chart(data=data[["Open","High", "Low", "Close"]])
    st.bar_chart(data=data["Volume"])





def main():
    with open("css/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown('''<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap" rel="stylesheet">''', unsafe_allow_html=True)

    tickers = pd.read_csv("csv/tickers.csv", encoding="ISO-8859-1")
    tickers.sort_values(by=['Name'], inplace=True)
    image = Image.open('logo/logo.png')
    st.sidebar.image(image)
    
    st.sidebar.title("YFinance!")
    org = st.sidebar.selectbox("Choose Listing:", tickers["Name"])
    symbol = tickers[tickers["Name"] == org]["Symbol"].values[0]
    final_calculation(symbol, org)
    

if __name__ == "__main__":
    st.set_page_config(
     page_title="Share Market App",
     page_icon="logo/logo.png",
     layout="wide",
     initial_sidebar_state="expanded",
 )


    main()
