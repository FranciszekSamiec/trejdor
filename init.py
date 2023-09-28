
import pandas as pd
import glob
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
import re
import libraries
from indicators import addVolume


frequency_options = {
    '1h': '1h',
    '1m': '1min',
    '1w': '1W',
}
# list of available pairs - used only in app layout
options = [
    'BTCBUSD',
    'ETHUSDT',
    'BTCDOWNUSDT',
    'ETHDOWNUSDT',
]

# Set the default selected option to "ETHUSDT"
selected_option = 'BTCBUSD'

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




def get_year_month_from_filename(filename):
    match = re.search(r'-(\d{4})-(\d{2})\.csv$', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return (year, month)
    else:
        return (0, 0)  # Return a default value for files with incorrect names


def makeDataFrame(path, dateBeginM, dateBeginY, dateEndM, dateEndY): 

    colnames=['Date','Open', 'High', 'Low', 'Close', 'Volume']

    file_list = glob.glob(path + "/*.csv")
    excel_list = []

    if len(file_list) == 0:
        print("No data available for this pair")
        return pd.DataFrame()

    sorted_files_by_year_month = sorted(file_list, key=lambda x: re.search(r'-(\d{4})-(\d{2})\.csv$', x).groups())

    begin_date_match = re.search(r'(\d{4}-\d{2}\.csv)', sorted_files_by_year_month[0])
    end_date_match = re.search(r'(\d{4}-\d{2}\.csv)', sorted_files_by_year_month[-1])



    begin_date_match = begin_date_match.group(1)
    end_date_match = end_date_match.group(1)
    print("cpicpia")

    file_list = sorted_files_by_year_month


    zeroBegin = ""
    zeroEnd = ""
    if len(str(dateBeginM)) == 1:
        zeroBegin = "0"

    if len(str(dateEndM)) == 1:
        zeroEnd = "0"

    begin = str(dateBeginY) + "-" + zeroBegin + str(dateBeginM) + ".csv"
    end = str(dateEndY) + "-" + zeroEnd + str(dateEndM) + ".csv"

    if begin > end:
        warning = "enter corect data"
        return warning

    print("begin: " + begin)
    print("end: " + end)


    print(begin_date_match)
    print(end_date_match)
    if begin < begin_date_match or end > end_date_match:
        warning = "No data available for this period. Available data from " + begin_date_match + " to " + end_date_match + "."
        return warning
    
    else:
        whetherToAppend = False

        for file in file_list:
            
            if file.endswith(begin):
                whetherToAppend = True
            
            if whetherToAppend:

                excel_list.append(pd.read_csv(file, header = None))

            if whetherToAppend == True and file.endswith(end):
                whetherToAppend = False
        

    df = pd.concat(excel_list)
    df.columns = colnames
    df = df.drop(0).reset_index(drop=True)

    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S')
    for column in df.iloc[:, 1:]:
        df[column] = df[column].astype(float)

    print(type(df.iloc[0]['Date']))

    return df

def availableRange(ticker):
    path = "./months/" + ticker
    file_list = glob.glob(path + "/*.csv")

    if len(file_list) == 0:
        print("No data available for this pair")
        return "this pair is not available"
    
    sorted_files_by_year_month = sorted(file_list, key=lambda x: re.search(r'-(\d{4})-(\d{2})\.csv$', x).groups())
    begin_date_match = re.search(r'(\d{4}-\d{2}\.csv)', sorted_files_by_year_month[0])
    end_date_match = re.search(r'(\d{4}-\d{2}\.csv)', sorted_files_by_year_month[-1])

    begin_date_match = begin_date_match.group(1)[:-4]
    end_date_match = end_date_match.group(1)[:-4]


    info = "Available data from " + begin_date_match+ " to " + end_date_match
    return info

def loadTicker(ticker, mBegin, yBegin, mEnd, yEnd):
    # load ticker from file
    
    path = "./months/" + ticker
    df = makeDataFrame(path, mBegin, yBegin, mEnd, yEnd)
    
    return df

def addVertialLoaders(fig, data):
    vertical_line_date_prev = data.iloc[0]['Date']
    vertical_line_date_next = data.iloc[-1]['Date'] # Replace with the date where you want the vertical line

    yMin = min(data['Low'])
    yMax = max(data['High'])


    if 1==1:# data.iloc[-1]['Date'].month == datetime.now().month and data.iloc[-1]['Date'].year == datetime.now().year:
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
                text="<",
                # textangle=90, 
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
                font=dict(size=12, color="white"),
                align="center",
                # captureevents=True,
                # hovertext="Double-lick to load another month",
                width=25,
                height=20,
                opacity=0.8,
            )
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
     
        fig.add_annotation(
            go.layout.Annotation(
                text=">",
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
                font=dict(size=12, color="white"),
                align="center",
                textangle=0,
                # captureevents=True,
                hovertext="Double-lick to load another month",
                width=25,
                height=20,
                opacity=0.8,
            )
        )

        fig.add_annotation(
            go.layout.Annotation(
                text="<",
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
                font=dict(size=12, color="white"),
                align="center",
                textangle=0,
                # captureevents=True,
                hovertext="Double-lick to load another month",
                width=25,
                height=20,
                opacity=0.8,
                yshift=30
            )
        )

    fig.add_trace(go.Scatter(
        x= [vertical_line_date_prev,vertical_line_date_prev],
        y=[0,1000000],
        mode='lines',
        name='Vertical Line',
        line=dict(color='blue', width=1),
        showlegend=False
    ))
    

    # fig.add_vline(x = vertical_line_date)





    fig.add_annotation(
        go.layout.Annotation(
            text="<",
            x=vertical_line_date_prev,
            # y=(data.iloc[0]['Low'] + data.iloc[0]['High']) / 2,
            y = 0.5,
            xref="x",
            yref="paper",
            showarrow=False,
            arrowhead=0,
            bgcolor="blue",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=12, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            hovertext="Double-lick to load earlier month",
            width=25,
            height=20,
            opacity=0.8,
        )
    )

    fig.add_annotation(
        go.layout.Annotation(
            text=">",
            x=vertical_line_date_prev,
            # y=((data.iloc[0]['Low'] + data.iloc[0]['High']) / 2),
            y = 0.5,
            xref="x",
            yref="paper",
            showarrow=False,
            arrowhead=0,
            bgcolor="blue",
            bordercolor="blue",
            borderwidth=2,
            font=dict(size=12, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            # hovertext="enter number of candles to load",
            width=25,
            height=20,
            opacity=0.8,
            yshift=30,
        )
    )
    
    # text_length = len(annotation_text)
    # width_multiplier = 8  # Adjust this value based on your needs
    # width = text_length * width_multiplier
    # print(min(fig['layout']['yaxis']))
    fig.add_annotation(
        go.layout.Annotation(
            text="100",
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
 
    

    yaxis_range = [yMin, yMax]  # Set the desired range
    fig.update_layout(yaxis=dict(range=yaxis_range))

def addCurrentPriceLine(fig, data):
    # last_candle = data[-1]
    last_candle = data.iloc[-1]['Close'] > data.iloc[-1]['Open']

    line_color = 'green' if last_candle else 'salmon'

    fig.add_shape(
        go.layout.Shape(
            type="line",
            xref="paper", 
            # x0=data.iloc[0]['Date'],
            x0 = 0,
            # x1=data.iloc[-1]['Date'], 
            x1 = 1,
            y0=data.iloc[-1]['Close'],  # Specify the horizontal line's y-coordinate
            y1=data.iloc[-1]['Close'],  # Specify the horizontal line's y-coordinate
            line=dict(color=line_color, width=0.8, dash='dot'),  # Line color, width, and style
        )
    )
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
    

def initCandlestickChart(data):

    fig = go.Figure(data=[go.Candlestick(x=data['Date'],
                                        open=data['Open'],
                                        high=data['High'],
                                        low=data['Low'],
                                        close=data['Close'])],
                                        )
    fig.update_layout(template=custom_theme)

    # Add custom layout
    fig.update_layout(
        title="",
        xaxis_rangeslider_visible=False,
        yaxis_autorange=False,
        margin = {
            'l': 0,
            'r': 125,
            'b': 0,
            't': 80,
        },
        yaxis_title="",
        xaxis_title=" ",
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
        spikemode="across",
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
    print(drawDowns)

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
