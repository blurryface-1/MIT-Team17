import streamlit as st 
import pandas as pd 
import plotly.graph_objects as go
import requests
from streamlit.elements.color_picker import ColorPickerMixin

df = pd.read_json('Stock List.json')
df = df[['date','symbol','open','close','high','low','volume']]

symbols = df['symbol'].unique()

st.write("""
# Financial Analytical Server 
""")
if 'history' not in st.session_state:
    st.session_state['history'] = []
def get_input():
    st.sidebar.header('User Input')
    start_date = st.sidebar.text_input('Start Date', '2021-04-01')
    end_date = st.sidebar.text_input('End Date', '2021-08-25')
    # stock_symbol = st.sidebar.text_input('Stock Symbol','AAPL')
    stock_symbol = st.sidebar.selectbox('Choose Option',symbols)
    st.header(f'{stock_symbol}')
    st.session_state.history.append(stock_symbol)
    return start_date, end_date, stock_symbol

def slice_it(symbol):
    dfm = df.loc[(df['symbol'])==symbol]
    # st.write(dfm.head(1))
    return dfm

def get_data(dfm, start ,end): 
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    start_row = 0
    end_row = 0

    for i in range(0,len(dfm)):
        if start <= pd.to_datetime(dfm['date'].iat[i]):
            start_row = i
            break

    for j in range(0,len(dfm)):
        if end >= pd.to_datetime(dfm['date'].iat[len(dfm)-1-j]):  #pd.to_datetime(
            end_row = len(dfm)-1-j
            break

    dfm = dfm.set_index(pd.DatetimeIndex(dfm['date'].values)) #pd.DatetimeIndex(dfm['date'].values))

    return dfm.iloc[start_row:end_row+1] 

def slider(fig):
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                    ])
                ),
            rangeslider=dict(
                visible=True),
            type="date"
        )
    )

def get_plot_ohlc(dfm,s):
    fig=go.Figure(data=[go.Ohlc(
        x=dfm['date'],
        open=dfm['open'], high=dfm['high'],
        low=dfm['low'], close=dfm['close'],
        increasing_line_color= '#00C5EB', decreasing_line_color= 'red',tickwidth=0.4
        )])

    fig.update_layout(
        title = s,height=500
    )
    slider(fig)
    return fig

def get_plot_candle(dfm,s):
    fig=go.Figure(data=[go.Candlestick(
        x=dfm['date'],
        open=dfm['open'], high=dfm['high'],
        low=dfm['low'], close=dfm['close'],
        increasing_line_color= '#00C5EB', decreasing_line_color= 'red',whiskerwidth=0.5,opacity=0.7
        )])
    fig.update_layout(
        title = s,height=500
    )
    slider(fig)
    return fig

def get_plot_line(dfm,s):
    fig = go.Figure(data=[go.Scatter(x=dfm['date'], y=dfm['high'])])
    fig.add_trace(go.Scatter(x=dfm['date'], y=dfm['low'], fillcolor='#00C5EB'))

    fig.update_layout(
        title = s,height=500
    )
    slider(fig)
    return fig

def company_info(symbol):
    symbol=symbol.lower()
    api_key="pk_8d58df2349d7433fb665fe5609363dcc"   # replace if credits over
    url="https://cloud.iexapis.com/stable/stock/"+symbol+"/company?token="+api_key    # uses iex cloud

    r=requests.get(url)
    cdata=r.json()
    companyName=str(cdata["companyName"])
    exchange=str(cdata["exchange"])
    industry=str(cdata["industry"])
    description=str(cdata["description"])
    ceo=str(cdata["CEO"])
    employees=str(cdata["employees"])

    total_desc="\nName: {}\n\nExchange: {}\n\nIndustry: {}\n\nCEO: {}\n\nNo. of Employees: {}\n\nDescription:\n{}\n".format(companyName,exchange,industry,ceo,employees,description)
    return total_desc

def remove_duplicates(arr):
    seen = set()
    seen_add = seen.add
    return [x for x in arr if not (x in seen or seen_add(x))]

start, end, symbol = get_input()

dfm = slice_it(symbol)

dfm = get_data(dfm, start, end)


if st.button('Information'):
    st.header(symbol + ' Information')
    st.write(company_info(symbol))


st.header('OHLC\n')
fig = get_plot_ohlc(dfm,symbol)
st.plotly_chart(fig)

st.header('Candlesticks\n')
fig = get_plot_candle(dfm,symbol)
st.plotly_chart(fig)

st.header('Line\n')
fig = get_plot_line(dfm,symbol)
st.plotly_chart(fig)

st.header('Volume\n')
st.line_chart(dfm['volume'])


st.header('Data Statistics')
st.write(dfm.head(10))



l = remove_duplicates(reversed(st.session_state.history))
for i in l:
    st.sidebar.write(i)
