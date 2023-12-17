from libraries import *
from indicators import *
import init # written this way to change the alue of global variables in
# init (right now only one - candles... = 100)
from init import *
from layout import createLayout
from eqChart import *
from api import *
import api # same story as with init - to change global variables in api
from dashboard import createDashBoard

# pydatetime deprecated warning, not a problem for now
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

#--------------------------------------------- GLOBAL VARIABLES
listOfPositions = []
isAddedPosition = False
count1 = 0
count2 = 0
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

categories = ['long maxouts', 'long < max', 'short maxouts', 'short < max']
longMaxouts = 1
longLessMax = 1
shortMaxouts = 1
shortLessMax = 1
lastCategory = ""





# right now app not timezone aware
timezone = pytz.timezone("Europe/Warsaw")
# says how many candles to load (from the current date) at the
# beginning of the app 


startDate = "2023-01-01 00:00:00"


timeframe = init.selected_frequency    

# num of candles to load at the beginning of the app
# but also when new pair is loaded or timeframe is changed
# ensures optimal range of data for every pair and timeframe
numOfCandlesToLoad = 2000
# these two lines make sure that the default date range for 
# every pair is current date - 2000 candles of whatever timeframe
# when new pair is loaded or timefram i changed 
# this will be the range for the new data
endDate = current_date_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
beginDate = findDateNCandlesBeforeDate(timeframe, endDate, numOfCandlesToLoad, "<")


app = dash.Dash(__name__)

#--------------------------------------------- GLOBAL VARIABLES




#-------------------------------------------------------------- INITIALIZATION
# data = makeDataFrame("./months/BTCBUSD", startM, startY, endM, endY)

data = makeDataFrame(selected_option, selected_frequency , beginDate, endDate)

# print(data)

occupiedCandle = [False] * len(data.index)
fig = initCandlestickChart(data)
addIndicators(data, fig)
equity_chart_fig = initEquityChart(equity_values)

occupiedCandle = [False] * len(data.index)

# Create the Dash app


info = availableRange(selected_option, selected_frequency)
# Define the layout of the app (in the layout.py file)
app.layout = createLayout(fig, options, frequency_options, selected_option, equity_chart_fig, info, "")
#-------------------------------------------------------------- INITIALIZATION




eqChart = dcc.Graph(
                        id='equity-chart',
                        figure=equity_chart_fig,
                        config={'displaylogo': False,'editable': True, 'responsive': True, 'scrollZoom': False},
                        style={
                            'transparent' : 'false',
                            'height': '100%',
                            'width': '100%'
                        }  # Set the chart height as 30% of the viewport height
                    )

@app.callback(Output('trading-eval', 'children'),
              [Input('url', 'pathname')],
            #   [Input('dummyTriggerDashboard', 'children')],
            )
def display_page(pathname):
    ctx = dash.callback_context
    triggered_by = ctx.triggered[0]['prop_id'] if ctx.triggered else None
    print("adasdasda")
    print(longMaxouts)


    pieChart = initPieChart(categories, [longMaxouts, longLessMax, shortMaxouts, shortLessMax])
    dashboard = createDashBoard(pieChart)

    if pathname == '/page-1':
        return dashboard
    else:
        if triggered_by == 'equity-chart.figure':
            return dash.no_update
        else:
            return eqChart



@app.callback(
    Output('dummyOutNewPos', 'children', allow_duplicate=True), 
    Input('options-percent-to-risk', 'value'),
    prevent_initial_call=True
)
def updatePercToRisk(newPerc):
    global perecentToRisk
    perecentToRisk = newPerc / 100
    return dash.no_update



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
    # ------ for dashboard

    # global longMaxouts
    # global longLessMax
    # global shortMaxouts
    # global shortLessMax




    x = indexOfEntryCandle + 1

    # print(endPrice, "endPrice ", entryPrice, "entryPrice ", stopLoss, " stopLoss", takeProfit, " takeProfit")



    while x < len(data.index) - 1 and x < indexOfEntryCandle + 24:

        # print(direction)
        if direction == 'long position':
    
            if data.iloc[x]['High'] >= takeProfit or data.iloc[x]['Low'] <= stopLoss:
                # endPrice = data.iloc[x]['Close']
                if data.iloc[x]['High'] >= takeProfit:
                    endPrice = takeProfit
                elif data.iloc[x]['Low'] <= stopLoss:
                    endPrice = stopLoss

                print("ebebe")
                break
        else:
            if data.iloc[x]['High'] >= stopLoss or data.iloc[x]['Low'] <= takeProfit:
                endPrice = data.iloc[x]['Close']
                break
        x = x + 1


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

    print(result, "result")



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



    if start_date is None or end_date is None:
        return dash.no_update
    
 
    resultOfLoad = loadTicker(selected_option, selected_frequency, start_date, end_date)
    if resultOfLoad.empty:
        return dash.no_update
    else:
        data = resultOfLoad


    occupiedCandle = [False] * len(data.index)
    listOfPositions = []

    fig = initCandlestickChart(data)

    addIndicators(data, fig)

    equity_values = [startCapital]
    equity_chart_fig = initEquityChart(equity_values)

    return fig

@app.callback(
    Output('candlestick-chart', 'figure', allow_duplicate=True), 
    Input('frequency-dropdown', 'value'),
    prevent_initial_call=True
)
def changeFrequency(selected_frequency):
    global data
    global fig
    global equity_chart_fig
    global equity_values
    global occupiedCandle
    global listOfPositions
    global timeframe 
    # global beginDate

    if selected_frequency is None:
        return dash.no_update

    beginDate = findDateNCandlesBeforeDate(selected_frequency, endDate, numOfCandlesToLoad, "<")
 
    resultOfLoad = loadTicker(selected_option, selected_frequency, beginDate, endDate)
    if resultOfLoad.empty:
        return dash.no_update
    else:
        data = resultOfLoad

    occupiedCandle = [False] * len(data.index)
    listOfPositions = []

    fig = initCandlestickChart(data)

    addIndicators(data, fig)

    equity_values = [startCapital]
    equity_chart_fig = initEquityChart(equity_values)

    timeframe = selected_frequency
    return fig

@app.callback(
    Output('candlestick-chart', 'figure', allow_duplicate=True),
    Output('equity-chart', 'figure', allow_duplicate=True), 
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

    info = availableRange(selected_option, selected_frequency)

    resultOfLoad = loadTicker(selected_option, selected_frequency, beginDate, endDate)
    if isinstance(resultOfLoad, str):
        return dash.no_update, dash.no_update
    else:
        data = resultOfLoad

    occupiedCandle = [False] * len(data.index)
    listOfPositions = []

    fig = initCandlestickChart(data)

    addIndicators(data, fig)

    equity_values = [startCapital]
    equity_chart_fig = initEquityChart(equity_values)

    return fig, equity_chart_fig
    

# for maxouts and less maxouts
def whichCategory(entryLevel, stopLoss, direction, percToRisk):


    tradePerc = abs(entryLevel - stopLoss) / entryLevel

    if direction == 'long':
        if tradePerc > percToRisk:
            return 'long maxouts'

        else:
            return 'long < max'
    else:
        if tradePerc > percToRisk:
            return 'short maxouts'
        else:
            return 'short < max'
        


def deleteLastCat(lastCategory):
    global longMaxouts
    global longLessMax
    global shortMaxouts
    global shortLessMax

    if lastCategory == 'long maxouts':
        longMaxouts = longMaxouts - 1
    elif lastCategory == 'long < max':
        longLessMax = longLessMax - 1
    elif lastCategory == 'short maxouts':
        shortMaxouts = shortMaxouts - 1
    elif lastCategory == 'short < max':
        shortLessMax = shortLessMax - 1


@app.callback(
    Output('equity-chart', 'figure', allow_duplicate=True),
    Output('dummyTriggerDashboard', 'children'),
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
    global perecentToRisk
    global lastCategory
    global count2



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

    x0 = roundDate(x0)  
    x1 = roundDate(x1)


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



    deleteLastCat(lastCategory)

    countMaxouts(listOfPositions[-1]['entryPrice'], listOfPositions[-1]['stopLoss'],
                    listOfPositions[-1]['direction'], perecentToRisk)


    if firstWasChangedShape:
        
        newVal = equity_values[-1]
        firstWasChangedShape = False

    equity_values[-1] = newVal + changeOfEquity

    updated_fig_relay = initEquityChart(equity_values)
    profitLossRegions = makeTracesToColorEqChart(startCapital, equity_values)
    useTracesToColor(profitLossRegions, updated_fig_relay)

    # updatedPiechart = initPieChart(categories, [longMaxouts, longLessMax, shortMaxouts, shortLessMax])

    count2 = (count2 + 1) % 3

    return [updated_fig_relay, dash.no_update]



def roundDate(date):
    if timeframe == '1m':
        result = roundDateToMinute(date)
    elif timeframe == '1h':
        result = roundDateToHour(date)
    elif timeframe == '1d':
        result = roundDateToDay(date)
    elif timeframe == '1w':
        result = roundDateToWeek(date)

    return result

def roundDateToHour(date_str):

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

def roundDateToMinute(date):
    
    input_date = parser.parse(date)
    seconds = input_date.second
    seconds_to_round = (60 - seconds) if seconds >= 30 else -seconds
    rounding_delta = timedelta(seconds=seconds_to_round)
    rounded_date = input_date + rounding_delta
    rounded_date = rounded_date.replace(microsecond=0)

    return rounded_date  # Return the datetime object

def roundDateToDay(date):
    input_date = parser.parse(date)
    hours = input_date.hour
    minutes = input_date.minute
    seconds = input_date.second

    hours_to_round = (24 - hours) if hours >= 12 else -hours
    rounding_delta = timedelta(hours=hours_to_round)
    rounded_date = input_date + rounding_delta
    rounded_date = rounded_date.replace(minute=0, second=0, microsecond=0)

    return rounded_date  # Return the datetime object

def roundDateToWeek(date):
    input_date = parser.parse(date)
    weekday = input_date.weekday()
    days_to_round = (7 - weekday) if weekday >= 3 else -weekday
    rounding_delta = timedelta(days=days_to_round)
    rounded_date = input_date + rounding_delta
    rounded_date = rounded_date.replace(hour=0, minute=0, second=0, microsecond=0)

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

        numberOfShape = -1
        entryDate = 0
        entryPrice = 0
        endDate = 0
        stopLoss = 0
        takeProfit = 0
        direction = ""
        # print(relayout_data, "<<<<<<<<<<<")

        for key, val in relayout_data.items():
            
            if type(val) == str:
                # val = roundDate(val)
                val = roundDate(val)


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

                # stopLoss = fig['layout']['shapes'][key_number]['y1']
                # takeProfit = fig['layout']['shapes'][key_number]['y1']
                
                # print(relayout_data)

                # print(fig['layout']['annotations'])
                # print("?")

                if property_name == 'x1':
                    if key_number % 2 == 1:
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                        numberOfShape = key_number - 1 # con be done only here because every rel has all coordinates
                        if fig['layout']['shapes'][numberOfShape]['y0'] <= fig['layout']['shapes'][numberOfShape]['y1']:
                            # short position
                            direction = "short"
                        elif fig['layout']['shapes'][numberOfShape]['y0'] > fig['layout']['shapes'][numberOfShape]['y1']:
                            # long position
                            direction = "long"
                    else:
                        fig['layout']['shapes'][key_number + 1][property_name] = val
                endDate = val    



                if property_name == 'x0':
   

                    if key_number % 2 == 1:
                        oldName = fig['layout']['shapes'][key_number - 1]['x0']
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                    else:
                        oldName = fig['layout']['shapes'][key_number + 1]['x0']
                        fig['layout']['shapes'][key_number + 1][property_name] = val

                    entryDate = val
                    # print(fig['layout']['annotations'])
                    # print(" ====================== ")
                    # print(oldName, " ", entryDate)
                    changeNameOfAnnotation(fig, oldName, entryDate)
                    # print(fig['layout']['annotations'])

                    # print(val, " +++++++ ", fig['layout']['shapes'][key_number - 1])


                if property_name == 'y0':

                    if key_number % 2 == 1:
                        fig['layout']['shapes'][key_number - 1][property_name] = val
                    else:
                        fig['layout']['shapes'][key_number + 1][property_name] = val
                    
                    entryPrice = val

                    # deleteAnnotation(fig, entryDate)
                    # addRRRatioAnnotation(fig, val, entryDate, endDate, stopLoss, takeProfit)

        color1 = fig['layout']['shapes'][numberOfShape]['fillcolor']

        if color1 == 'Salmon':
            stopLoss = fig['layout']['shapes'][numberOfShape]['y1']
            takeProfit = fig['layout']['shapes'][numberOfShape + 1]['y1']       
        elif color1 == 'Green':
            takeProfit = fig['layout']['shapes'][numberOfShape]['y1']
            stopLoss = fig['layout']['shapes'][numberOfShape + 1]['y1']


        # entry DAte is id of annotation
        deleteAnnotation(fig, entryDate)
        addRRRatioAnnotation(fig, entryPrice, entryDate, endDate, stopLoss, takeProfit)    
        


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
            global_result = makeAdjustedRelayout(fig, relayout_data)

    
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
    # print(relayout_data)
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

    # print(startDate, " <<<<>>>> ", endDate)

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

# have to round to hours minutes etc
def getIndexFromDate(date):

    global timeframe

    if date < data.iloc[0]['Date']:
        return 0
    elif date > data.iloc[len(data.index) - 1]['Date']:
        return len(data.index) - 1
    # print(date)
    test = data['Date'].tolist()
    # test = test.sort()
    test = sorted(test)
    # print(test)
    # date  = date.timestamp()
    # print(test)
    date = pd.Timestamp(date)

    # print(type(data.iloc[0]['Date']), " ", type(date))
    # print(timeframe)
    if timeframe == '1m':
        freq = 'T'
    elif timeframe == '1h':
        freq = 'H'
    elif timeframe == '1d':
        freq = 'D'
    elif timeframe == '1w':
        freq = 'W'
    
    if timeframe != '1w':
        date = date.floor(freq)
    else:
        date = date.week

    # print(len(data.index))

    # print(type(timestampDate))
    for index in range(0, len(data.index)):
        # print(data.iloc[index]['Date'], " ", date)
        if timeframe != '1w':
            flooredDate = data.iloc[index]['Date'].floor(freq)
        else:
            flooredDate = data.iloc[index]['Date'].week
        # print(flooredDate, " <", date)

        if flooredDate == date:
            # print("znalaz")
            return index

def findMinMaxValues(start, end):

    # if start == end:
    #     return [0,0]
    res = []

    subset_df = data.iloc[start:end + 1]

    min = subset_df['Low'].min()
    max = subset_df['High'].max()
        
    res.append(min)
    res.append(max)

    return res    

def makeAdjustedRelayout(fig, relayout_data):

    # if autorange return relayout_data and do not proceed
  
    if isAutoSized(relayout_data):
        # print("gggurba")
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
    print(start, end, "%")
    startIndex = getIndexFromDate(start)
    endIndex = getIndexFromDate(end)

    if startIndex == endIndex:
        return relayout_data

    # print(startIndex, endIndex, "$$$$$$$")
    minMax = findMinMaxValues(startIndex, endIndex)

    margin = calculateTopBottomMargin(minMax[0], minMax[1])
    adjustedRel['xaxis.range[0]'] = start
    adjustedRel['xaxis.range[1]'] = end
    adjustedRel['yaxis.range[0]'] = minMax[0] - margin
    adjustedRel['yaxis.range[1]'] = minMax[1] + margin

    filteredData = data.iloc[startIndex:endIndex]

    # print(max(filteredData['Volume']))
    fig.update_layout(
        yaxis2_range=[0, max(filteredData['Volume']) * 2],
    )

    return adjustedRel


def getDatesFromRelayoutData(relayout_data):
    datesRes = []

    for key, val in relayout_data.items():
        
        # print(key)

        if type(val) == str:
            # val = roundDate(val)
            val = roundDate(val)
            datesRes.append(val)

    return datesRes

# five kinds of annotations:
# [0] - load new candles right end of chart
# [1] - hide candles right end of chart
# [2] - number of candles right end of chart
# [3] - hide candles left end of chart
# [4] - load past candles left end of chart
# [5] - number of candles left end of chart
def getNumberOfCandlesfromAnnotation(relayout_data):
    first_key = getFirstKeyOfRelayoutData(relayout_data)

    number = relayout_data[first_key]
    number = int(number)

    return number 

def whatKindOfAnnotation(relayout_data):

    first_value = next(iter(relayout_data.values()))

    # exception for dashed line when up to date, stupid af i know
    if first_value == "←":
        return "< right"

    # print(relayout_data)
    first_key = getFirstKeyOfRelayoutData(relayout_data)
    pattern = r'\[(\d+)\]'
    match = re.search(pattern, first_key)
    if match:
        # Extract the matched number from the regex match
        extracted_number = match.group(1)
        # Convert the extracted number to an integer

        if extracted_number == '0':
            return "> right"
        elif extracted_number == '1':
            return "< right"
        elif extracted_number == '2':
            return "num right"
        elif extracted_number == '3':
            return "> left"
        elif extracted_number == '4':
            return "< left"
        elif extracted_number == '5':
            return "num left"
        else:
            return "not annotation"
    else:
        return "not annotation"



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
    global timeframe

    print(relayout_data)

    if not isClickedAnnotation(relayout_data):
        return dash.no_update
    else:
        kindOfAnnotation = whatKindOfAnnotation(relayout_data)


        if kindOfAnnotation == "> right":
            dateBegin = data.iloc[-1]['Date']

            dateEnd = findDateNCandlesBeforeDate(timeframe, dateBegin, init.candlesToLoadwithVerticalLine, ">")
            dateBegin = dateBegin.strftime('%Y-%m-%d %H:%M:%S')

            newData = makeDataFrame(selected_option, selected_frequency, dateBegin, dateEnd)
            data = pd.concat([data,newData])
            occupiedCandle.extend([False] * len(newData)) 

        elif kindOfAnnotation == "< right":

            dateBegin = data.iloc[-1]['Date']
            dateEnd = findDateNCandlesBeforeDate(timeframe, dateBegin, init.candlesToLoadwithVerticalLine, "<")
            dateBegin = dateBegin.strftime('%Y-%m-%d %H:%M:%S')



            if dateEnd < data.iloc[0]['Date'].strftime('%Y-%m-%d %H:%M:%S'):
                return dash.no_update
            # end and begin switched places because we want to hide candles
            mask = (data['Date'] > dateBegin) | (data['Date'] < dateEnd)
            newLen = len(data) - len(data[mask])
            data = data[mask]

            occupiedCandle = occupiedCandle[:-newLen]
            # newData = makeDataFrame(selected_option, selected_frequency, dateEnd, dateBegin)
        elif kindOfAnnotation == "num right":
            print("good")
            init.candlesToLoadwithVerticalLine = getNumberOfCandlesfromAnnotation(relayout_data)

        elif kindOfAnnotation == "< left":

            dateEnd = data.iloc[0]['Date']
            dateBegin = findDateNCandlesBeforeDate(timeframe, dateEnd, init.candlesToLoadwithVerticalLine, "<")
            dateEnd = dateEnd.strftime('%Y-%m-%d %H:%M:%S')

   

            newData = makeDataFrame(selected_option, selected_frequency, dateBegin, dateEnd)
            data = pd.concat([newData, data])
            occupiedCandle = [False] * len(newData) + occupiedCandle
        
        elif kindOfAnnotation == "> left":
            # print("good")
            dateBegin = data.iloc[0]['Date']
            dateEnd = findDateNCandlesBeforeDate(timeframe, dateBegin, init.candlesToLoadwithVerticalLine, ">")
            dateBegin = dateBegin.strftime('%Y-%m-%d %H:%M:%S')

            if dateEnd > data.iloc[-1]['Date'].strftime('%Y-%m-%d %H:%M:%S'):
                return dash.no_update

            mask = (data['Date'] < dateBegin) | (data['Date'] > dateEnd)
            newLen = len(data) - len(data[mask])

            data = data[mask]
            occupiedCandle = occupiedCandle[newLen:]
        elif kindOfAnnotation == "num left":
            init.candlesToLoadwithVerticalLine = getNumberOfCandlesfromAnnotation(relayout_data)



        fig1 = fig
        # print(data.columns)
        fig = initCandlestickChart(data)
        addIndicators(data, fig)

        for shape in fig1["layout"]["shapes"]:
            fig.add_shape(shape)

        global_result = makeAdjustedRelayout(fig, relayout_data)

        if 'xaxis.range[0]' in global_result:
            fig['layout']['xaxis']['range'] = [
                global_result['xaxis.range[0]'],
                global_result['xaxis.range[1]']
            ]

        if 'yaxis.range[0]' in global_result:
            fig['layout']['yaxis']['range'] = [
                global_result['yaxis.range[0]'],
                global_result['yaxis.range[1]']
            ]

        fig.update_layout(
            dragmode = 'pan',
        )

        return fig


def countMaxouts(entryLevel, stopLoss, percToRisk, direction): 
    global longMaxouts
    global shortMaxouts
    global longLessMax
    global shortLessMax
    global lastCategory

    tradePerc = abs(entryLevel - stopLoss) / entryLevel
    if direction == 'long':
        if tradePerc > percToRisk:
            longMaxouts += 1
        else:
            longLessMax += 1
    else:
        if tradePerc > percToRisk:
            shortMaxouts += 1
        else:
            shortLessMax += 1
    
    lastCategory = whichCategory(entryLevel, stopLoss, direction, percToRisk)
        


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
    global perecentToRisk

    #------ for dashboard
    global longMaxouts
    global shortMaxouts
    global longLessMax
    global shortLessMax



    # print()
    print(clickData)
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
            endOfShape = 0
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

            # print(fig['layout']['shapes'])

            addRRRatioAnnotation(fig, clicked_candle['Close'], clicked_candle['Date'],
                                  data.iloc[endOfShape]['Date'], newPos['stopLoss'],
                                    newPos['takeProfit'])
            # print(fig['layout']['annotations'])

            firstWasChangedShape = True
            listOfPositions.append(newPos)

            countMaxouts(newPos['entryPrice'], newPos['stopLoss'], perecentToRisk, newPos['direction'])

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
            
            longMaxouts = 0
            shortMaxouts = 0
            longLessMax = 0
            shortLessMax = 0

            isAddedPosition = False


            occupiedCandle = [False] * len(data.index)

            deleteAllRRRatioAnnotations(fig)
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
        global_result = makeAdjustedRelayout(fig, relayout_data)

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
    

def changeNameOfAnnotation(fig, entryDate, newName):
    annotations_list = list(fig['layout']['annotations'])



    for annotation in annotations_list:
        # print(annotation)
        if annotation['name'] == str(entryDate):
            # print("deleted")
            # print(annotation['name'], entryDate ," <<<<<----", annotation['x'])
            # print(annotations_list)
            annotation['name'] = str(newName)
            # print(annotations_list)
            # break

    fig['layout']['annotations'] = annotations_list

def deleteAllRRRatioAnnotations(fig):
    annotations_list = list(fig['layout']['annotations'])


    newListOfAnnotations = []
    for annotation in annotations_list:
        if annotation['name'] == None:
            newListOfAnnotations.append(annotation)
            # annotations_list.remove(annotation)



    fig['layout']['annotations'] = newListOfAnnotations



def deleteAnnotation(fig, entryDate):


    annotations_list = list(fig['layout']['annotations'])



    for annotation in annotations_list:
        # print(annotation)
        if annotation['name'] == str(entryDate):
            # print("deleted")
            # print(annotation['name'], entryDate ," <<<<<----", annotation['x'])
            # print(annotations_list)
            annotations_list.remove(annotation)
            # print(annotations_list)
            # break
            
                
    # fig.update_layout(annotations=annotations_list)
    # dont know why but line above does some stranger shit, i wasted 10 fucking hours on it 
    # dash is a fucking piece of shit
    fig['layout']['annotations'] = annotations_list



# name is used to identify pair annotation with its position - long/short rectangle shape
# as a name date is used
def addRRRatioAnnotation(fig, entryPrice, entryDate, endDate, stopLoss, takeProfit):



    RRratio = abs(takeProfit - entryPrice) / abs(entryPrice - stopLoss)

    fig.add_annotation(
        go.layout.Annotation(
            name= str(entryDate),
            text="RR ratio: " + str(round(RRratio, 2)),
            x = entryDate + ( endDate - entryDate) / 2,
            y = entryPrice,
            xref="x",
            yref="y", 
            showarrow=False,
            arrowhead=0,
            bgcolor="#323738",
            bordercolor="blue",
            borderwidth=1,
            font=dict(size=9, color="white"),
            align="center",
            textangle=0,
            # captureevents=True,
            hovertext="enter number of candles to load",
            width=70,
            height=15,
            opacity=1,
            # yshift=-35,
        )
    )


@app.callback(
    Output('dummyOutNewPairSearch', 'children', allow_duplicate=True),
    Output('new-pair-info', 'children', allow_duplicate=True),
    Output('new-pair-info', 'style', allow_duplicate=True),
    Input('new-pair', 'value'),
    prevent_initial_call=True,
)
def printSearching(value):
    print(value)
    if value == "":
        return dash.no_update, dash.no_update, dash.no_update
    else:
        return value, "searching...", {'color': 'blue',
                                        'max-width': '100px',
                                        'overflow-y': 'auto',
                                        'font-family': 'sans-serif',

                                        }

@app.callback(
    # Output('plusMinusButton', 'children', allow_duplicate=True),
    Output('new-pair-info', 'children', allow_duplicate=True),
    Output('new-pair-info', 'style', allow_duplicate=True),
    Input('dummyOutNewPairSearch', 'children'),
    State('new-pair', 'value'),
    prevent_initial_call=True,
) 
def readNewPairInput(dummyTrigger ,newPairInput):
    print(newPairInput)
    # newPair = newPairInput

    if isSymbolListedOnBinance(newPairInput):
        print("jest")
        return "symbol available", {'color': '#42c8f5',
                                        'max-width': '80px',
                                        'overflow-y': 'auto',
                                        'font-family': 'sans-serif',

                                        }
    else:
        print("nie ma")

        return "symbol not available", {'color': 'orange',
                                        'max-width': '80px',
                                        'overflow-y': 'auto',
                                        'font-family': 'sans-serif',

                                        }






@app.callback(
    # Output('plusMinusButton', 'children', allow_duplicate=True),
    Output('chart-title-dropdown', 'options'),
    Input('plus-button', 'n_clicks'),
    Input('minus-button', 'n_clicks'),
    State('new-pair-info', 'style'),
    State('new-pair', 'value'),
    prevent_initial_call=True,
)
def addDeletePairs(plus_clicks, minus_clicks, style, newPairInput):

    triggered_input = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

    if newPairInput == "":
        return dash.no_update

    if not style:
        return dash.no_update, dash.no_update
    elif style['color'] == '#42c8f5':
        print("blue")
        if triggered_input == 'plus-button':
            print("plus")
            symbol = newPairInput.replace("/", "")
            if not symbol in api.app_data['symbols']:
                api.app_data['symbols'].append(symbol)
                newPair = 'symbol', 'newPairInput'
                api.symbolTranslation[newPair[0]] = newPair[1]
                init.options.append(symbol)
                
                # check()

            # return "added", init.options
        elif triggered_input == 'minus-button':
            print("minus--------")



            symbol = newPairInput.replace("/", "")
            if symbol in api.app_data['symbols']:
                api.app_data['symbols'].remove(symbol)
                newPair = 'symbol', 'newPairInput'
                api.symbolTranslation.pop(newPair[0])
                init.options.remove(symbol)
                # check()
            # return "deleted", init.options

        api.create_data_folders_and_files(api.app_data)
    return init.options
    

@app.callback(
    Output('candlestick-chart', 'figure'),
    Input('candlestick-chart', 'hoverData'),
    prevent_initial_call=True,
)   
def displayHoverData(hoverData):
    if hoverData is not None:
        # print(hoverData)
        # x_value = hoverData['points'][0]['x']
        # y_value = hoverData['points'][0]['y']

        # annotation = {
        #     'x': x_value,
        #     'y': y_value,
        #     'xref': 'x',
        #     'yref': 'y',
        #     'text': f'x: {x_value}, y: {y_value}',
        #     'showarrow': True,
        #     'arrowhead': 2,
        #     'arrowcolor': 'red',
        #     'arrowwidth': 2,
        #     'bordercolor': 'red',
        #     'borderwidth': 2,
        #     'borderpad': 4,
        #     'bgcolor': 'white',
        #     'opacity': 0.8
        # }

        # fig.layout.annotations.append(annotation)

        # return fig
        return dash.no_update

    else:
        return dash.no_update



# @app.callback(
#     Output('candlestick-chart', 'figure', allow_duplicate=True),
#     Input('candlestick-chart', 'hoverData'),
#     State('candlestick-chart', 'figure'),
#     prevent_initial_call=True,
# )
# def display_hover_data(hoverData, figure):
#     print(hoverData)
#     x = hoverData.get('points')[0]['x']
#     # y = hoverData.get('points')[0]['y']

#     # fig.add_annotation(
#     #     go.layout.Annotation(
#     #         text= data.iloc[-1]['Close'],# + data.iloc[-1]['Date'],
#     #         # textangle=90, 
#     #         xref = "paper",
#     #         x=0.5,
#     #         # y=((data.iloc[-1]['Low'] + data.iloc[-1]['High']) / 2),
#     #         y = y,
#     #         yref="y",
#     #         showarrow=False,
#     #         arrowhead=0,
#     #         bgcolor="red",
#     #         bordercolor="red",
#     #         borderwidth=2,
#     #         font=dict(size=12, color="white"),
#     #         align="center",
#     #         # captureevents=True,
#     #         # hovertext="Double-lick to load another month",
#     #         width=20,
#     #         height=25,
#     #         opacity=1,
#     #     )
#     # )

#     # add annotations to figure
#     # figure['layout'].update(
#     #     {
#     #         'annotations': [
#     #             {
#     #                 'xref': 'x',
#     #                 'yref': 'paper',
#     #                 'showarrow': False,
#     #                 'text': f'x:{x}',
#     #                 'x': 1,
#     #                 'y': 1,
#     #             },
#     #             {
#     #                 'xref': 'paper',
#     #                 'yref': 'y',
#     #                 'showarrow': False,
#     #                 'text': f'y:{y}',
#     #                 'x': -0.15,
#     #                 'y': y,
#     #             },
#     #         ]
#     #     }
#     # )
#     return dash.no_update



#     return dash.no_update

if __name__ == '__main__':
    app.run_server(debug = True, host="127.0.0.1", port="8050")


