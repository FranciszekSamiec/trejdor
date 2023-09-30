# needed to import data because when adding indicator i add it also to global
# dataframe as a new column
# needed global fig because i add indicator to it as a new trace
from libraries import *
import pandas as pd

listOfIndicators = {'vwap': 'blue',
                     'hh': 'green',
                    'll': 'green'}

def highestHigh(length, dataFrame):
    df = dataFrame
    highestHigh = []
    highestHigh.append(df.iloc[0, 2])
    count = 1
    df = dataFrame
    for x in range(1, len(dataFrame.index)):
        if count == length: 
            highestHigh.append(df.iloc[x, 2])
            count = 0
        else:
            highestHigh.append(max(highestHigh[-1], df.iloc[x, 2]))
            if highestHigh[-2] < df.iloc[x, 2]:
                count = 0
        count = count + 1
    return highestHigh

def lowestLow(length, dataFrame):
    df = dataFrame
    lowestLow = []
    lowestLow.append(df.iloc[0, 3])
    count = 1
    for x in range(1, len(dataFrame.index)):
        if count == length:
            lowestLow.append(df.iloc[x, 3])
            count = 0
        else:
            lowestLow.append(min(lowestLow[-1], df.iloc[x, 3]))
            if lowestLow[-2] > df.iloc[x, 3]:
                count = 0
        count = count + 1
    return lowestLow

def vwap(df):
    typicalPrice = []
    cumVol = []
    cumVol.append(df.iloc[0, 5])
    cumTypPrice = []
    vwap = []


    for x in range(0, len(df.index)):
        typicalPrice.append((df.iloc[x, 2] + df.iloc[x, 3] + df.iloc[x, 4]) / 3)


    for x in range(0, len(df.index)):
        typicalPrice[x] = typicalPrice[x] * df.iloc[x, 5] 
        


    cumTypPrice.append(typicalPrice[0])

    vwap.append(cumTypPrice[0] / cumVol[0])

    for x in range(1, len(df.index)):
        if (df.iloc[x,0].hour == 1):
            cumVol.append(df.iloc[x, 5])
            cumTypPrice.append(typicalPrice[x])
        else:
            cumVol.append(cumVol[x-1] + df.iloc[x, 5])
            cumTypPrice.append(cumTypPrice[x - 1] + typicalPrice[x])
        vwap.append(cumTypPrice[x] / cumVol[x])

    return vwap

# used during initialization of candlestick chart
def addVolume(data, fig): 

    colors = []

    for i in range(len(data.Close)):
        if i != 0:
            if data.iloc[i]['Close'] > data.iloc[i-1]['Close']:
                colors.append('green')
            else:
                colors.append('salmon')
        else:
            colors.append('salmon')

    fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'],
                     marker=dict(opacity = 0.4, color=colors, line=dict(width=0)),
                     yaxis='y2', name='Volume'))
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price',
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False),
        title='Candlestick Chart with Volume Bars'
    )

    # adjustor = 

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Price',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            range=[0, max(data['Volume']) * 1]  # Adjust the range for the volume y-axis
        ),
        # Adjust the range for the volume y-axis
        # yaxis2_range=[0, np.mean(data['Volume']) * 20],
        yaxis2_range=[0, max(data['Volume']) * 2],

        title='Candlestick Chart with Volume Bars',

    )

    return fig

# adds both to dataframe and figure. have to remember to add indicators after selecting 
# new pair
def addIndicator(dataFrame, fig, indicatorSeries, nameOfIndicator, colorOfIndicator):
    # global data

    # print(global_variables.data)

    dataFrame[nameOfIndicator] = indicatorSeries

    fig.add_trace(go.Scatter(
        x=dataFrame['Date'],
        y=indicatorSeries,
        mode='lines',
        line=dict(color=colorOfIndicator, width=0.7),
        name=nameOfIndicator
    ))

# only indicators line like - not volume
def addIndicators(dataFrame, fig):
    for name, color in listOfIndicators.items():
        if name == 'vwap':
            addIndicator(dataFrame, fig, vwap(dataFrame), name, color)
        elif name == 'hh':
            addIndicator(dataFrame, fig, highestHigh(20, dataFrame), name, color)
        elif name == 'll':
            addIndicator(dataFrame, fig, lowestLow(20, dataFrame), name, color) 

def is_global_dataframe(df):
    # Get the list of global variables
    global_vars = globals()

    # Iterate through global variables and compare their values
    for var_name, var_value in global_vars.items():
        if var_value is df:
            return True
    return False
