from libraries import *
from indicators import *
from init import *
from layout import createLayout
from eqChart import *
# from api import *

#--------------------------------------------- GLOBAL VARIABLES
listOfPositions = []
isAddedPosition = False
count1 = 0 
equity_values = []
startCapital = 100000
perecentToRisk = 0.02
equity_values = [startCapital]
prevCapital = startCapital
firstWasChangedShape = True # needed to know if changing position so as to 
                        # not to update equity chart every time after reshaping
                        # because the same capital will be added many times
                        # NEEDED TO KNOW IF FIRST TIME OF CHANGING SHAPE
newVal = 0  # first time of changing shape - needed to know what is the value of equity
            # before reshaping so as to add to it the change of equity after reshaping
global_result = {} # stores current relayoutdata
show_dropdown = False


data = None # candlestick chart
fig = go.Figure([]) # candlestick chart
equity_chart_fig = None # equity chart
listOfEquityValues = {} # dictionary of equity values - differeent for every pair
# TODO make different equity charts for different pairs

# list of candles which are occupied by position rectangle
# needed to prevent adding more than one rectangle to the same candle
occupiedCandle = []
wasRadioChanged = False
prevRadio = 'long position'
lastRelDataOfZoom = {}
count = 0 # needed to cause change to dummy so as to trigger callback: displayclickdata

timezone = pytz.timezone("Europe/Warsaw")
# says how many candles to load (from the current date) at the
# beginning of the app 
defaultLookBackPer = 1488 
currentDate = datetime.now(timezone).date()
beginDate = currentDate - timedelta(hours=defaultLookBackPer)

startM = beginDate.month 
startY = beginDate.year
endM = currentDate.month
endY = currentDate.year

startDate = "2023-01-01 00:00:00"

app = dash.Dash(__name__)

#--------------------------------------------- GLOBAL VARIABLES

print("a dla was ja ni kto")



#-------------------------------------------------------------- INITIALIZATION
data = makeDataFrame("./months/BTCBUSD", startM, startY, endM, endY)

print(type(data.iloc[0]['Date']))

occupiedCandle = [False] * len(data.index)
fig = initCandlestickChart(data)
addIndicators(data, fig)
equity_chart_fig = initEquityChart(equity_values)

occupiedCandle = [False] * len(data.index)

# Create the Dash app


info = availableRange(selected_option)
# Define the layout of the app (in the layout.py file)
app.layout = createLayout(fig, options, frequency_options, selected_option, equity_chart_fig, info)
#-------------------------------------------------------------- INITIALIZATION
# app.clientside_callback(
#     """
#     document.getElementById('candlestick-chart').on('plotly_afterplot', function() {
#         var annotation = document.getElementById('annotation-id');
#         annotation.addEventListener('plotly_click', function() {
#             // Handle the click event on the annotation here
#             alert('Annotation clicked!'); // Example action
#             // You can load another month of data or perform any desired action.
#         });
#     });
#     """
# )



def isChangedShape(relayoutData):
    # write function which checks whether dictionary relayoutData has key which name starts with 'shapes'
    # if it has then return True else return False
    if relayoutData is None:
        return False
    
    first_key = str(next(iter(relayoutData.keys())))

    if first_key.startswith('shapes'):
        return True
    else:
        return False




def executePosition(direction, indexOfEntryCandle, entryPrice, endPrice, stopLoss, takeProfit):
    global startCapital
    # looking for candle hitting stop loss or take profit before 24 candles
    
    x = indexOfEntryCandle + 1


    while x < len(data.index) - 1 and x < indexOfEntryCandle + 24:

        # print(direction)
        if direction == 'long position':
    
            if data.iloc[x]['High'] >= takeProfit or data.iloc[x]['Low'] <= stopLoss:
                endPrice = data.iloc[x]['Close']
                break
        else:
            if data.iloc[x]['High'] >= stopLoss or data.iloc[x]['Low'] <= takeProfit:
                endPrice = data.iloc[x]['Close']
                break
        x = x + 1

    # print(x)

    if x < indexOfEntryCandle + 24:
        if direction == 'long position':
            if data.iloc[x]['Low'] <= stopLoss:
                endPrice = data.iloc[x]['Low']
            elif data.iloc[x]['High'] >= takeProfit:
                endPrice = data.iloc[x]['High']
        else:
            if data.iloc[x]['High'] >= stopLoss:
                endPrice = data.iloc[x]['High']
            elif data.iloc[x]['Low'] <= takeProfit:
                endPrice = data.iloc[x]['Low']


    result = 0
    if direction == 'long position':
        earningPerc = (endPrice - entryPrice) / entryPrice
        losingPerc = (entryPrice - endPrice) / entryPrice
        earningPercTakeProf = (takeProfit - entryPrice) / entryPrice
        lossPercStopLoss = (entryPrice - stopLoss) / entryPrice 

        tradeCapital = (startCapital * perecentToRisk) / lossPercStopLoss 
        tradeCapital = min(tradeCapital, startCapital)

        if endPrice > takeProfit or endPrice < stopLoss:
            if endPrice > takeProfit:

                result = (earningPercTakeProf) * tradeCapital

            elif endPrice < stopLoss:
                result = (lossPercStopLoss) * tradeCapital * (-1)
        else:
            if endPrice > entryPrice:
                result = (earningPerc) * tradeCapital
            elif endPrice < entryPrice:
                result = (losingPerc) * tradeCapital * (-1)
    else:
        earningPerc = (entryPrice - endPrice) / entryPrice
        losingPerc = (endPrice - entryPrice) / entryPrice
        earningPercTakeProf = (entryPrice - takeProfit) / entryPrice
        lossPercStopLoss = (stopLoss - entryPrice) / entryPrice 

        tradeCapital = (startCapital * perecentToRisk) / lossPercStopLoss 
        tradeCapital = min(tradeCapital, startCapital)

        if endPrice < takeProfit or endPrice > stopLoss:
            if endPrice < takeProfit:
                result = (earningPercTakeProf) * tradeCapital 
            elif endPrice > stopLoss:
                result = (lossPercStopLoss) * tradeCapital * (-1)
        else:
            if endPrice < entryPrice:
                result = (earningPerc) * tradeCapital
            elif endPrice > entryPrice:
                result = (losingPerc) * tradeCapital * (-1)


    return result
        

# test = executePosition('long', 100, 110, 90, 120)







def useTracesToColor(profitLossRegions, updated_fig):

    greenTraceX = profitLossRegions[0]
    breakEvenTraceX = profitLossRegions[1]
    redTraceX = profitLossRegions[2]
    
    greenTraceY = profitLossRegions[3]
    breakEvenTraceY = profitLossRegions[4]
    redTraceY = profitLossRegions[5]


    # print(greenTrace)
    # print(breakEvenTrace)
    # print(redTrace)


    green_area_trace = go.Scatter(
        x=greenTraceX,
        y=greenTraceY,
        fill='tonexty',
        fillcolor='rgba(255, 0, 0, 0.1)',
        showlegend=False,
        line=dict(color='rgba(0,0,0,0)', width=0),
    )

    red_area_trace = go.Scatter(
        x=breakEvenTraceX,
        y=breakEvenTraceY,
        fill='tonexty',
        fillcolor='rgba(0, 128, 0, 0.1)',
        showlegend=False,
        line=dict(color='rgba(0,0,0,0)', width=0),
    )

    noneAreaTrace = go.Scatter(
        x=redTraceX,
        y=redTraceY,
        fill='none',
        showlegend=False,
        line=dict(color='rgba(0,0,0,0)', width=0),
    )

    updated_fig.add_trace(green_area_trace)
    updated_fig.add_trace(red_area_trace)
    updated_fig.add_trace(noneAreaTrace)

    makeRedLine(redTraceY, redTraceX, updated_fig)


def is_whole_number(number):
    return number == round(number)
    

def makeRedLine(redTraceY, redTraceX, updated_fig_relay):
    redLineY = []
    redLineX = []

    for a, b in zip(redTraceY, redTraceX):


        if a < startCapital:   
            redLineY.append(a)
            redLineX.append(b)


        elif a == startCapital and not is_whole_number(b):
            redLineY.append(a)
            redLineX.append(b)


        elif len(redTraceY) >= 2: 
            if b == 0: 
                redLineY.append(a)
                redLineX.append(b)


    if len(redLineY) >= 2:
        for a, b, c, d in zip(redLineY, redLineY[1:], redLineX, redLineX[1:]):

            if not (a == startCapital and b == startCapital):

                singleTraceY = []
                singleTraceX = []
                singleTraceY.append(a)
                singleTraceY.append(b)
                singleTraceX.append(c)
                singleTraceX.append(d)
                # print(b)
                redLine = go.Scatter(
                    x=singleTraceX,
                    y=singleTraceY,
                    mode='lines',
                    line=dict(color='red', width=0.7),
                    name='Equity'
                )
                updated_fig_relay.add_trace(redLine)

    

@app.callback(
    Output('candlestick-chart', 'figure', allow_duplicate=True), 
    Output('error', 'children'), 
    Input('dateStart', 'date'),
    Input('dateEnd', 'date'),
    prevent_initial_call=True
)    
def changeDateRange(start_date, end_date):
    global data
    global fig
    global equity_chart_fig
    global equity_values
    global occupiedCandle
    global listOfPositions
    global startM
    global startY
    global endM
    global endY


    if start_date is None or end_date is None:
        return dash.no_update, ''
    
    
    startM = int(start_date[5:7])
    startY = int(start_date[0:4])
    endM = int(end_date[5:7])
    endY = int(end_date[0:4])

    resultOfLoad = loadTicker(selected_option, startM, startY, endM, endY)
    if isinstance(resultOfLoad, str):
        return dash.no_update, resultOfLoad
    else:
        data = resultOfLoad


    occupiedCandle = [False] * len(data.index)
    listOfPositions = []

    fig = initCandlestickChart(data)

    addIndicators(data, fig)

    equity_values = [startCapital]
    equity_chart_fig = initEquityChart(equity_values)

    return fig, ''

@app.callback(
    Output('candlestick-chart', 'figure', allow_duplicate=True),
    Output('equity-chart', 'figure', allow_duplicate=True), 
    Output('error', 'children', allow_duplicate=True),  
    Input('chart-title-dropdown', 'value'),
    prevent_initial_call=True
      # Input from the dropdown menu
)
def changePair(selected_option):
    # Depending on the selected_option, generate a new figure for the candlestick chart
    # You can replace this part with your actual chart generation logic
    global data
    global fig
    global equity_chart_fig
    global equity_values
    global occupiedCandle
    global listOfPositions

    data = data.drop(data.index)

    info = availableRange(selected_option)

    resultOfLoad = loadTicker(selected_option, startM, startY, endM, endY)
    if isinstance(resultOfLoad, str):
        return dash.no_update, dash.no_update, info
    else:
        data = resultOfLoad

    occupiedCandle = [False] * len(data.index)
    listOfPositions = []

    fig = initCandlestickChart(data)

    addIndicators(data, fig)

    equity_values = [startCapital]
    equity_chart_fig = initEquityChart(equity_values)

    return fig, equity_chart_fig, info
    


@app.callback(
    Output('equity-chart', 'figure', allow_duplicate=True),  # Output to update the candlestick chart
    Input('dummyOutNewPos', 'children'),
    Input('candlestick-chart', 'relayoutData'),
    State('equity-chart', 'figure'),
    prevent_initial_call=True
)
def update_equity_chart(children, relayoutData, equity_chart_fig):

    global equity_values
    global isAddedPosition
    global firstWasChangedShape
    global newVal

    updated_fig = initEquityChart(equity_values)
    profitLossRegions = makeTracesToColorEqChart(startCapital, equity_values)
    useTracesToColor(profitLossRegions, updated_fig)

    if len(listOfPositions) == 0:
        return updated_fig


    if isAddedPosition:
        isAddedPosition = False

        return updated_fig   

    if not isChangedShape(relayoutData):
        return dash.no_update
    
    x1 = 0
    y0 = 0
    y1 = 0
    x0 = 0

    for key, val in relayoutData.items():
        if key.endswith('x1'):
            x1 = val
        elif key.endswith('y0'):
            y0 = val
        elif key.endswith('y1'):
            y1 = val
        elif key.endswith('x0'):
            x0 = val

    x0 = round_to_nearest_hour(x0)  
    x1 = round_to_nearest_hour(x1)


    listOfPositions[-1]['entryDate'] = x0
    listOfPositions[-1]['entryPrice'] = y0
    listOfPositions[-1]['endPrice'] = y1
    listOfPositions[-1]['endDate'] = x1

    if listOfPositions[-1]['direction'] == 'long position':

        if y1 > y0:
            listOfPositions[-1]['takeProfit'] = y1
        else:
            listOfPositions[-1]['stopLoss'] = y1

    else:

        if y1 < y0:
            listOfPositions[-1]['takeProfit'] = y1
        else:
            listOfPositions[-1]['stopLoss'] = y1
        

    changeOfEquity = executePosition(listOfPositions[-1]['direction'], 
                    listOfPositions[-1]['index'], listOfPositions[-1]['entryPrice'],
                    listOfPositions[-1]['endPrice'],
                    listOfPositions[-1]['stopLoss'],
                    listOfPositions[-1]['takeProfit'])


    if firstWasChangedShape:
        
        newVal = equity_values[-1]
        firstWasChangedShape = False

    equity_values[-1] = newVal + changeOfEquity

    updated_fig_relay = initEquityChart(equity_values)
    profitLossRegions = makeTracesToColorEqChart(startCapital, equity_values)
    useTracesToColor(profitLossRegions, updated_fig_relay)


    return updated_fig_relay


def round_to_nearest_hour(date_str):

    input_date = parser.parse(date_str)

    # Calculate the minutes and seconds
    minutes = input_date.minute
    seconds = input_date.second

    # Calculate the number of minutes needed to round to the nearest hour
    minutes_to_round = (60 - minutes) if minutes >= 30 else -minutes

    # Create a timedelta with the calculated minutes
    rounding_delta = timedelta(minutes=minutes_to_round)

    # Round the input date to the nearest hour
    rounded_date = input_date + rounding_delta

    # Zero out seconds and milliseconds
    rounded_date = rounded_date.replace(second=0, microsecond=0)

    return rounded_date  # Return the datetime object


@app.callback(
    Output('dummyOut', 'children'),
    Input('candlestick-chart', 'relayoutData')
)
def updateChart(relayout_data):

    global count

    # if change was not in shapes then no updating of dummy 
    # so it doesnt trigger displayclickdata
    if isChangedShape(relayout_data):

        for key, val in relayout_data.items():
            
            if type(val) == str:
                # val = roundDate(val)
                val = round_to_nearest_hour(val)


            key_parts = key.split('.')
            key_number_match = re.search(r'\[(\d+)\]', key_parts[0])
            if key_number_match:
                
                key_number = int(key_number_match.group(1))
                property_name = key_parts[1]
                # print(f"{key_number}, {property_name}, {val};")
                # now update fig layout with new values
                fig['layout']['shapes'][key_number][property_name] = val

                Out = str(key_number) + ' ' + str(property_name) + ' ' + str(val)
                # print(Out)
                
                if property_name == 'x1':
                    if key_number % 2 == 1:
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                    else:
                        fig['layout']['shapes'][key_number + 1][property_name] = val

                if property_name == 'x0':
                    
                    if key_number % 2 == 1:
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                    else:
                        fig['layout']['shapes'][key_number + 1][property_name] = val

                if property_name == 'y0':

                    if key_number % 2 == 1:
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                    else:
                        fig['layout']['shapes'][key_number + 1][property_name] = val
            

        # modulo division is to avoid over int limit
        # also it is needed to caouse change to dummy so it triggers callback: displayclickdata
        # because it has dummy as input
        count = (count + 1) % 3
        return count

    return dash.no_update 




# this is callback to track last relayout data which didnt involve changing shape
# only resizing chart or zooming
@app.callback(
    Output('relayout-data', 'children'),
    Input('candlestick-chart', 'relayoutData')
)
def keepingTrackOfLastRel(relayout_data):
    global global_result
    if relayout_data is not None:
        if not isChangedShape(relayout_data):
            # global_result = copy.deepcopy(relayout_data)
            global_result = makeAdjustedRelayout(relayout_data)

    
    return str(global_result)

# functions to find what kind of relayout data is it
# ther are 4? types: shape, range, autorange, dragmode
def getFirstKeyOfRelayoutData(relayout_data):
    if relayout_data is None:
        return -69
    
    first_key = str(next(iter(relayout_data.keys())))
    return first_key

def isChangedZoom(relayout_data):

    first_key = getFirstKeyOfRelayoutData(relayout_data)

    return first_key.startswith('xaxis.range')

def isAutoSized(relayout_data):

    first_key = getFirstKeyOfRelayoutData(relayout_data)

    return first_key.startswith('xaxis.autorange')

def isDragmode(relayout_data):

    first_key = getFirstKeyOfRelayoutData(relayout_data)

    return first_key.startswith('dragmode')

def isClickedAnnotation(relayout_data):
    first_key = getFirstKeyOfRelayoutData(relayout_data)

    return first_key.startswith('annotations')


#--------------------------------------------------------------

def autoRangeRelayout():
    # find date od the first candle and date of the last candle
    # find min and max value of yaxis
    # return relayout_data with those values
    adjustedRel = {}

    startDate = data.iloc[0]['Date']
    endDate = data.iloc[len(data.index) - 1]['Date']



    maxVal = data['High'].max()
    minVal = data['Low'].min()

    margin = calculateTopBottomMargin(minVal, maxVal)

    adjustedRel['xaxis.range[0]'] = startDate
    adjustedRel['xaxis.range[1]'] = endDate
    adjustedRel['yaxis.range[0]'] = minVal - margin
    adjustedRel['yaxis.range[1]'] = maxVal + margin

    return adjustedRel

def calculateTopBottomMargin(minVal, maxVal):
    # calculate top and bottom margin
    # if difference between min and max is less than 10 then margin is 10% of min
    # else margin is 10% of difference between min and max

    margin = (maxVal - minVal) * 0.1

    return margin

def getIndexFromDate(date):
    if date < data.iloc[0]['Date']:
        return 0
    elif date > data.iloc[len(data.index) - 1]['Date']:
        return len(data.index) - 1
    
    for index in range(0, len(data.index)):
        if data.iloc[index]['Date'] == date:
            return index

def findMinMaxValues(start, end):
    res = []

    subset_df = data.iloc[start:end + 1]

    min = subset_df['Low'].min()
    max = subset_df['High'].max()
        
    res.append(min)
    res.append(max)

    return res    

def makeAdjustedRelayout(relayout_data):

    # if autorange return relayout_data and do not proceed
  
    if isAutoSized(relayout_data):
        return autoRangeRelayout()   
    
    if not isChangedZoom(relayout_data):
        return global_result


    adjustedRel = {}

    dates = getDatesFromRelayoutData(relayout_data)
    start = dates[0]
    end = dates[1]
    # print("#####")
    # print(end)
    # print(endIndex)
    startIndex = getIndexFromDate(start)
    endIndex = getIndexFromDate(end)

    minMax = findMinMaxValues(startIndex, endIndex)

    margin = calculateTopBottomMargin(minMax[0], minMax[1])
    adjustedRel['xaxis.range[0]'] = start
    adjustedRel['xaxis.range[1]'] = end
    adjustedRel['yaxis.range[0]'] = minMax[0] - margin
    adjustedRel['yaxis.range[1]'] = minMax[1] + margin

    return adjustedRel


def getDatesFromRelayoutData(relayout_data):
    datesRes = []

    for key, val in relayout_data.items():
        
        # print(key)

        if type(val) == str:
            val = round_to_nearest_hour(val)
            datesRes.append(val)

    return datesRes

# used to capture clicking on vertical loaders
# here you should also add possibility to change period of skipping 
@app.callback(
    Output('candlestick-chart', 'figure', allow_duplicate = True),
    Input('candlestick-chart','relayoutData'),
    prevent_initial_call = True
)
def loadNewData(relayout_data):
    global data
    global selected_option
    global fig
    global occupiedCandle


    dateBegin = data.iloc[-1]['Date']
    beginM = dateBegin.month + 1
    if beginM == 13:
        beginM = 1
        beginY = dateBegin.year + 1
    else:
        beginY = dateBegin.year

    dateEnd = dateBegin + relativedelta(months = 1)
    endM = dateEnd.month
    endY = dateEnd.year
    # print("tuuute")
    # print(beginM)
    # print(endY)
    # print(selected_option)
    # print(beginM)
    # print(beginY)

    path = "./months/" + selected_option


    # print(type(dateBegin))
    if not isClickedAnnotation(relayout_data):
        return dash.no_update
    else:
        # print(data)
        newData = makeDataFrame(path, beginM, beginY, endM, endY)
        # print("\/\/\/\/\/")
        # print(newData)
        # print(" ")
        # print(data)
        # print(" ")

        occupiedCandle.extend([False] * len(newData)) 
        # print(data['Volume'])
        # print(newData['Volume'])
        # print(newData.columns)
        data = pd.concat([data,newData])
        fig1 = fig
        print(data)
        print("/\/\/\/\/")
        # print(data.columns)
        fig = initCandlestickChart(data)
        addIndicators(data, fig)

        for shape in fig1["layout"]["shapes"]:
            fig.add_shape(shape)


        

        return fig



# occupiedCandle = [False] * len(data.index)
# Define the callback to capture click events and update the chart
@app.callback(
    [Output('candlestick-chart', 'figure', allow_duplicate=True),
     Output('dummyOutNewPos', 'children')],
    [Input('candlestick-chart', 'clickData'),
     Input('refresh-button', 'n_clicks'),
     State('position', 'value'),
     Input('dummyOut', 'children')],
    [Input('candlestick-chart', 'relayoutData')],
    prevent_initial_call=True

)
def display_click_data(clickData, n_clicks, value, children, relayout_data):
    ctx = dash.callback_context
    # print(dash.callback_context.triggered[0]['prop_id'].split('.')[1])

    point_index = None
    global occupiedCandle
    global wasRadioChanged
    global prevRadio
    global lastRelDataOfZoom
    global listOfPositions
    global isAddedPosition
    global count1
    global equity_values
    global startCapital
    global prevCapital
    global firstWasChangedShape
    print(relayout_data)
    # print()
    # print(clickData)
    if value != prevRadio:
        wasRadioChanged = True
        prevRadio = value
    else:
        wasRadioChanged = False


    triggered_by = ctx.triggered[0]['prop_id'] if ctx.triggered else None


    if clickData is not None and triggered_by != "candlestick-chart.relayoutData":# and wasRadioChanged == False: <<<<<???? i added this but dont remember why, !may be bug later!

        point_index = clickData['points'][0]['pointIndex']
        clicked_candle = data.iloc[point_index]


        # add to the chart rectangle which has one corner in close of the clicked candle and the other corner in the close of the next candle
        # checking argument "value" if long then adding long position shape else adding short position shape
        if not occupiedCandle[point_index]:

            if point_index + 24 > len(data.index) - 1:
                endOfShape = len(data.index) - 1
            else:
                endOfShape = point_index + 24
                
            if value == 'long position':
                # loss rectangle

                fig.add_shape(
                    editable=True,
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=clicked_candle['Date'],
                    x1=data.iloc[endOfShape]['Date'],
                    y1=data.iloc[point_index]['ll'],
                    y0=data.iloc[point_index]['Close'],
                    line=dict(    
                        color="IndianRed",
                        width=2,
                    ),
                    fillcolor="Salmon",
                    opacity=0.4,
                )
                # profit rectangle

                fig.add_shape(
                    editable = True,
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=clicked_candle['Date'],
                    x1=data.iloc[endOfShape]['Date'],
                    y1=data.iloc[point_index]['Close'] + (data.iloc[point_index]['Close'] - data.iloc[point_index]['ll']),
                    y0=data.iloc[point_index]['Close'],
                    line=dict(
                        color="Green",
                        width=2,
                    ),
                    fillcolor="Green",
                    opacity=0.3,
                )

                newPos = {
                    'index': point_index,
                    'entryDate': clicked_candle['Date'],
                    'entryPrice': clicked_candle['Close'],
                    'stopLoss': data.iloc[point_index]['ll'],
                    'takeProfit': data.iloc[point_index]['Close'] + (data.iloc[point_index]['Close'] - data.iloc[point_index]['ll']),
                    'direction': value
                }

            else:
                # loss rectangle for short
                fig.add_shape(
                    editable=True,
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=clicked_candle['Date'],
                    x1=data.iloc[endOfShape]['Date'],
                    y1=data.iloc[point_index]['hh'],
                    y0=data.iloc[point_index]['Close'],
                    line=dict(
                        color="IndianRed",
                        width=2,
                    ),
                    fillcolor="Salmon",
                    opacity=0.5,
                )
                fig.add_shape(
                    editable = True,                    
                    type="rect",
                    xref="x",
                    yref="y",
                    x0=clicked_candle['Date'],
                    x1=data.iloc[endOfShape]['Date'],
                    y1=data.iloc[point_index]['Close'] - (data.iloc[point_index]['hh'] - data.iloc[point_index]['Close']),
                    y0=data.iloc[point_index]['Close'],
                    line=dict(
                        color="Green",
                        width=2,
                    ),
                    fillcolor="Green",
                    opacity=0.3,
                )
                newPos = {
                    'index': point_index,
                    'entryDate': clicked_candle['Date'],
                    'entryPrice': clicked_candle['Close'],
                    'stopLoss': data.iloc[point_index]['hh'],
                    'takeProfit': data.iloc[point_index]['Close'] - (data.iloc[point_index]['hh'] - data.iloc[point_index]['Close']),
                    'direction': value
                }
            
            # print all vaues from exwcutPos 
     


            firstWasChangedShape = True
            listOfPositions.append(newPos)

            newEq = prevCapital + executePosition(value,point_index, newPos['entryPrice'], 
                                                 data.iloc[endOfShape]['Close'], 
                                                 newPos['stopLoss'], 
                                                 newPos['takeProfit'])
            # print(newEq)
            equity_values.append(newEq)
            prevCapital = newEq
            isAddedPosition = True

        occupiedCandle[point_index] = True        

    if relayout_data:

        if ctx.triggered[0]['prop_id'] == 'refresh-button.n_clicks':
            listOfPositions = []
            prevCapital = startCapital
            equity_values = [startCapital]

            isAddedPosition = False


            occupiedCandle = [False] * len(data.index)
            # if len(occupiedCandle) > 0:
            if point_index is not None:
                occupiedCandle[point_index] = True
            clickData = None

            

            # print(fig)
            if 'shapes' in fig['layout']:
                fig['layout']['shapes'] = []

        if isDragmode(relayout_data):

            fig.update_layout(dragmode=relayout_data['dragmode'])  # You can set it to 'zoom', 'pan', 'select', or 'lasso'
            # return dash.no_update, dash.no_update


        fig1 = copy.deepcopy(fig)
        # print(isChangedShape(relayout_data))
        # print(relayout_data)
        global_result = makeAdjustedRelayout(relayout_data)

        if 'xaxis.range[0]' in global_result:
            fig1['layout']['xaxis']['range'] = [
                global_result['xaxis.range[0]'],
                global_result['xaxis.range[1]']
            ]

        if 'yaxis.range[0]' in global_result:
            fig1['layout']['yaxis']['range'] = [
                global_result['yaxis.range[0]'],
                global_result['yaxis.range[1]']
            ]
            fig1.update_layout(
                # title=ticker,
                xaxis_rangeslider_visible = False,
                yaxis_autorange=False,
                xaxis_title="",
                yaxis_title="",
            )
        
        
        
        count1 = (count1 + 1) % 3
        return fig1, count1
            

    return fig, count1


if __name__ == '__main__':
    app.run_server(debug = True, host="127.0.0.1", port="8050")

