
from libraries import *
from indicators import addVolume


frequency_options = {
    '1m': '1min',
    '1h': '1h',
    '1d': '1D',
    '1w': '1W',
}
# list of available pairs - used only in app layout
options = [
    'BTCBUSD',
    'ETHUSDT',
    'BTCDOWNUSDT',
    'ETHDOWNUSDT',
]


candlesToLoadwithVerticalLine = 100
# Set the default timeframe and pair
selected_option = 'BTCBUSD'
selected_frequency = '1h'

#  color theme for both charts (candlestick and equity curve)
custom_theme = {
    'layout': {
        'plot_bgcolor': '#131722',  # Set the background color of the plot area
        'paper_bgcolor': '#131722',  # Set the background color of the entire graph
        'font': {
            'color': 'white'  # Set the font color of text elements
        },
        'xaxis': {
            'gridcolor': '#343144'  # Set the color of the x-axis grid lines
        },
        'yaxis': {
            'gridcolor': '#343144'  # Set the color of the y-axis grid lines
        }
        # You can add more custom styling properties as needed
    }
}    


def printInfo():
    print(candlesToLoadwithVerticalLine)

def get_year_month_from_filename(filename):
    match = re.search(r'-(\d{4})-(\d{2})\.csv$', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return (year, month)
    else:
        return (0, 0)  # Return a default value for files with incorrect names

def makeDataFrame(symbol, timeframe, beginDate, endDate):
    colnames=['Date','Open', 'High', 'Low', 'Close', 'Volume']
    
    output_folder = './months/' + symbol + '/'
    print(output_folder)
    csv_file = f'{output_folder}{symbol}-{timeframe}.csv'
    # Read the entire CSV file into a DataFrame
    df = pd.read_csv(csv_file, names=colnames, header=0)
    print(df)
    # Convert the 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Filter the DataFrame based on the specified date range
    print(beginDate)
    print(endDate)

    mask = (df['Date'] >= beginDate) & (df['Date'] <= endDate)
    filtered_df = df.loc[mask]
    print(filtered_df)
    return filtered_df



def availableRange(symbol, timeframe):

    colnames=['Date','Open', 'High', 'Low', 'Close', 'Volume']
    output_folder = './months/' + symbol + '/'
    csv_file = f'{output_folder}{symbol}-{timeframe}.csv'
    # Read the entire CSV file into a DataFrame
    df = pd.read_csv(csv_file, names=colnames, header=0)
    # file_list = glob.glob(path + "/*.csv")
    if len(df) > 0:
        begin_date_match = df.iloc[0]['Date']
        end_date_match = df.iloc[-1]['Date']
    else:
        return "this pair is not available"


    info = "Available data from " + begin_date_match + " to " + end_date_match
    return info


def loadTicker(symbol, timeframe, dateBegin, dateEnd):
    # load ticker from file
    
    # path = "./months/" + ticker
    df = makeDataFrame(symbol, timeframe, dateBegin, dateEnd)
    
    return df

def checkIfUpToDate(data, timeframe):
    lastDate = pd.to_datetime(data.iloc[-1]['Date'])

    today = datetime.utcnow()
    if timeframe == "1m":
        truncated_date = lastDate.replace(second=0, microsecond=0)
        truncated_today = today.replace(second=0, microsecond=0)
    elif timeframe == "1h":
        truncated_date = lastDate.replace(minute=0, second=0, microsecond=0)
        truncated_today = today.replace(minute=0, second=0, microsecond=0)
    elif timeframe == "1d":
        truncated_date = lastDate.replace(hour=0, minute=0, second=0, microsecond=0)
        truncated_today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    elif timeframe == "1w":
        truncated_date = lastDate.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
        truncated_today = today.replace(day=0, hour=0, minute=0, second=0, microsecond=0)
    else:
        print("error in checkIfUpToDate")
        return False
    
    return truncated_date == truncated_today

def addAnnotationRespForNumberOfCandles(fig, vertical_line_date_prev):
    global candlesToLoadwithVerticalLine

    fig.add_annotation(
        go.layout.Annotation(
            text=candlesToLoadwithVerticalLine,
            x=vertical_line_date_prev,
            y = 0,
            xref="x",
            yref="paper", 
            showarrow=False,
            arrowhead=0,
            bgcolor="#323738",
            bordercolor="blue",
            borderwidth=1,
            font=dict(size=12, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            hovertext="enter number of candles to load",
            width=35,
            height=30,
            opacity=1,
            # yshift=-35,
        )
    )

def addArrowAnnotations(fig, xVal):
    vertical_line_date_next = xVal
    fig.add_annotation(
        go.layout.Annotation(
            text="→",
            x=vertical_line_date_next,
            # y=((data.iloc[-1]['Low'] + data.iloc[-1]['High']) / 2),
            y = 0.5,
            xref="x",
            yref="paper",
            showarrow=False,
            arrowhead=0,
            bgcolor="blue",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=10, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            hovertext="Double-click to load/hide candles",
            width=16,
            height=35,
            opacity=0.8,
        )
    )
    
    fig.add_annotation(
        go.layout.Annotation(
            text="←",
            x=vertical_line_date_next,
            # y=((data.iloc[-1]['Low'] + data.iloc[-1]['High']) / 2),
            y = 0.5,
            xref="x",
            yref="paper",
            showarrow=False,
            arrowhead=2,
            bgcolor="blue",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=10, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            hovertext="Double-cick to load/hide candles",
            width=16,
            height=35,
            opacity=0.8,
            yshift=45,
        )
    )
    

def addVertialLoaders(fig, data):

    vertical_line_date_prev = data.iloc[0]['Date']
    vertical_line_date_next = data.iloc[-1]['Date'] # Replace with the date where you want the vertical line

    yMin = min(data['Low'])
    yMax = max(data['High'])


    if checkIfUpToDate(data, selected_frequency):
        fig.add_trace(go.Scatter(
            x= [vertical_line_date_next,vertical_line_date_next],
            y=[0,1000000],
            mode='lines',
            name='Vertical Line',
            line=dict(dash= 'dash',color='blue', width=1), 
            showlegend=False
        ))
        
        fig.add_annotation(
            go.layout.Annotation(
                text="←",
                # textangle=90, 
                x=vertical_line_date_next,
                # y=((data.iloc[-1]['Low'] + data.iloc[-1]['High']) / 2),
                y = 0.5,
                xref="x",
                yref="paper",
                showarrow=False,
                arrowhead=2,
                bgcolor="blue",
                bordercolor="blue",
                borderwidth=2,
                font=dict(size=12, color="white"),
                align="center",
                # captureevents=True,
                hovertext="Double-click to hide candles",
                width=16,
                height=35,
                opacity=0.8,
            )
        )
        fig.add_annotation(
            name = "dummy",
            visible=False,
        )
    else:

        fig.add_trace(go.Scatter(
            x= [vertical_line_date_next,vertical_line_date_next],
            y=[0,1000000],
            mode='lines',
            name='Vertical Line',
            line=dict(color='blue', width=1), 
            showlegend=False
        ))
     
        addArrowAnnotations(fig, vertical_line_date_next)

    addAnnotationRespForNumberOfCandles(fig, vertical_line_date_next)


    fig.add_trace(go.Scatter(
        x= [vertical_line_date_prev,vertical_line_date_prev],
        y=[0,1000000],
        mode='lines',
        name='Vertical Line',
        line=dict(color='blue', width=1),
        showlegend=False
    ))

    addArrowAnnotations(fig, vertical_line_date_prev)
    
    # text_length = len(annotation_text)
    # width_multiplier = 8  # Adjust this value based on your needs
    # width = text_length * width_multiplier
    # print(min(fig['layout']['yaxis']))
 

    addAnnotationRespForNumberOfCandles(fig, vertical_line_date_prev)


    yaxis_range = [yMin, yMax]  # Set the desired range
    fig.update_layout(yaxis=dict(range=yaxis_range))


def addCurrentPriceLine(fig, data):
    # last_candle = data[-1]
    last_candle = data.iloc[-1]['Close'] > data.iloc[-1]['Open']

    line_color = 'green' if last_candle else 'salmon'

# Create the horizontal line trace
    horizontal_line_trace = go.Scatter(
        x=[data.iloc[0]['Date'], data.iloc[-1]['Date'] + pd.DateOffset(years=3)],  # Extend the line by 30 days (adjust as needed)
        y=[data.iloc[-1]['Close'], data.iloc[-1]['Close']], 
        # x=data['Date'],  # Specify the x-values for the horizontal line (dates)
        # y=[data.iloc[-1]['Close']] * len(data),  # Create a list of the same y-value (closing price)
        mode='lines',
        line=dict(color=line_color, width=0.8, dash='dot'),  # Line color, width, and style
        name='Horizontal Line',
        showlegend=False
    )

    fig.add_trace(horizontal_line_trace)  # Add the horizontal line trace to the figure

    text_length = len(str(data.iloc[-1]['Close']))
    width_multiplier = 7  # Adjust this value based on your needs
    width = text_length * width_multiplier
    fig.add_annotation(
        go.layout.Annotation(
            text= data.iloc[-1]['Close'],# + data.iloc[-1]['Date'],
            # textangle=90, 
            xref = "paper",
            x=1.04,
            # y=((data.iloc[-1]['Low'] + data.iloc[-1]['High']) / 2),
            y = data.iloc[-1]['Close'],
            yref="y",
            showarrow=False,
            arrowhead=0,
            bgcolor=line_color,
            bordercolor=line_color,
            borderwidth=2,
            font=dict(size=12, color="white"),
            align="center",
            # captureevents=True,
            # hovertext="Double-lick to load another month",
            width=width,
            height=25,
            opacity=1,
        )
    )
    x_axis_range = [data.iloc[0]['Date'], data.iloc[-1]['Date']]  # Set the desired range
    fig.update_layout(xaxis=dict(range=x_axis_range))




def initCandlestickChart(data):

    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'],
                                        name='ohlc',
                                        # hoverinfo='x+y',
                                        )],
                                        )
    fig.update_layout(template=custom_theme)

    # # Add custom layout
    fig.update_layout(
        title="",
        hovermode='closest',
        xaxis_rangeslider_visible=False,
        yaxis_autorange=False,
        # this is very interesting, it causes problems with scrolling zoom
        # making it shaking everything, 
        # margin = {
        #     'l': 0,
        #     # 'r': 0,
        #     # 'b': 0,
        #     # 't': 0,
        # },
        yaxis_title="",
        xaxis_title=" ",
        legend = dict(
            orientation="h",
            # yanchor="bottom",
            y=1.22,
            # xanchor="right",
            x=0.38,
            bordercolor = "#323738",
            borderwidth = 1.2,
            xref = "paper",
            yref = "paper",
        ),
        dragmode = 'pan',
    )
    pio.templates.default = "plotly_dark"

    fig = addVolume(data, fig)

    fig.update_yaxes(zerolinewidth=1, zerolinecolor='gray')
    fig.update_xaxes(showgrid=True)


    addVertialLoaders(fig, data)
    addCurrentPriceLine(fig, data)

    fig.update_xaxes(
        showspikes=True,
        spikecolor="grey",
        spikesnap="cursor",
        spikemode="toaxis+across+marker",
        spikedash="dash",
        spikethickness=0.7
    )

    fig.update_yaxes(
        showspikes=True,
        spikecolor="grey",
        spikesnap="cursor",
        spikemode="across",
        spikedash="dash",
        spikethickness=0.7

    )

    return fig

def calculateDrawdown(equity):
    max_equity = 0  # Initialize the maximum equity to zero
    drawdowns = []  # Create an empty list to store drawdown values

    for value in equity:
        if value > max_equity:
            max_equity = value  # Update the maximum equity if a new peak is reached
        drawdown = max_equity - value  # Calculate the drawdown
        drawdowns.append(drawdown)  # Append the drawdown to the list

    result = [x * (-1) for x in drawdowns]

    return result



def initEquityChart(equity_values):
# Create the initial equity chart figure

    drawDowns = calculateDrawdown(equity_values)
    # drawDowns = (-1) * drawDowns
    if max(equity_values):
        base = max(equity_values)
    else:
        base = 0

    updated_fig = go.Figure(
        data=[
            go.Scatter(
                x=list(range(len(equity_values))),
                y=equity_values,
                mode='lines',
                line=dict(color='green', width=0.7),
                name='Equity'
            )
        ],
        # layout=dict(template="plotly_dark")  # Apply dark mode template to this chart
    )

    updated_fig.add_trace(go.Bar(x=list(range(len(drawDowns))), y=drawDowns,
                    marker=dict(opacity = 0.2, color='blue', line=dict(width=0)),
                    yaxis='y2', name='drawdown', base = 0))
    
    updated_fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price',
        # yaxis2=dict(title='drawdown', overlaying='y', side='right', showgrid=False),
        title='eq chart',
        yaxis2=dict(
            showgrid=False,
            title='drawdown',
            overlaying='y',
            side='right',
            range=[min(drawDowns) * 2, 0]  # Adjust the range for the drawdown y-axis
        ),
        bargap = 0.05,
        # bargroupgap=0.1    # Set the gap between bar groups

    )

    margin = {
        'l': 0,
        'r': 20,
        'b': 0,
        't': 60,
    }

    updated_fig.update_layout(
        title='Equity chart',
        xaxis_rangeslider_visible=False,
        yaxis_autorange=True,
        yaxis_title="",
        xaxis_title="",
        margin = margin,
        showlegend=False,
        template = custom_theme
    )

    
    updated_fig.update_xaxes(showgrid=True)


    return updated_fig


# def triggerAllInits():
#     # global data
#     # global equity_chart_fig   
#     # global equity_values


def initPieChart(labels, values):

    fig = go.Figure(
        data=[go.Pie(labels=labels, values=values)],
        layout=go.Layout(title='Pie Chart', template=custom_theme)
    )


    return fig