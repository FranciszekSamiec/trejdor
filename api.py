from libraries import * 


global app_data
app_data = {
    'symbols': ['BTCBUSD', 'BTCDOWNUSDT', 'ETHUSDT', 'ETHDOWNUSDT'],  # Replace with your list of symbols
    'timeframes': ['1m', '1h', '1d' ,'1w'],  # Replace with your list of timeframes
}

candlesToLoad = {
    '1m': 26280,
    '1h': 8760,
    '1d': 365,
    '1w': 52,
}

# used to translat symbol for valid format on binance
# later maybe used for other exchanges
symbolTranslation = {
    'BTCBUSD': 'BTC/USDT',
    'ETHUSDT': 'ETH/USDT',
    'ETHDOWNUSDT': 'ETHDOWN/USDT',
    'BTCDOWNUSDT': 'BTCDOWN/USDT',
}



binance = ccxt.binance({
    'rateLimit': 1200,  # Adjust the rate limit as needed
})
target_timezone = pytz.timezone("EUROPE/Warsaw")
all_data = pd.DataFrame()
# if there is no file for certain pair and timeframe than it is created 
# and data downloaded beginning from this arbitrary date 
# ultimateBeginDate = "2021-01-01 00:00:00" 



def parseSymbol(symbol):
    new_symbol = symbol.replace('/', '')
    return new_symbol

# symbol = 'BTC/BUSD'  # Example trading pair (Bitcoin/USDT)
# symbol = parseSymbol(symbol)  # Update the symbol here


# TODO make it work for all timezones
def download_historical_data(startDate, symbol, timeframe):
    # start_date = pd.to_datetime("2023-01-01 00:00:00")

    print("startDate", startDate)

    start_date = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')

    # start_date = start_date - timedelta(hours=1)
    
    start_date = start_date.astimezone(pytz.UTC)
    start_date = start_date.astimezone(pytz.UTC).replace(tzinfo=None)

    print("startDate2", startDate)


    # start_date = pd.to_datetime(startDate)
    end_date = datetime.now()
    all_data = pd.DataFrame()

    while start_date <= end_date:
        since = int(start_date.timestamp() * 1000)
        until = int(end_date.timestamp() * 1000)
    
        symbolBinance = symbolTranslation.get(symbol)
        candles = binance.fetch_ohlcv(symbolBinance, timeframe, since=since, limit=1000)


        # Check rate limit headers in the response
        # limit = binance.response.headers.get('x-ratelimit-limit')
        # remaining = binance.response.headers.get('x-ratelimit-remaining')
        # reset_time = binance.response.headers.get('x-ratelimit-resettime')


        # print(f"Rate Limit: {limit}")
        # print(f"Remaining Requests: {remaining}")
        # print(f"Reset Time (Unix Timestamp): {reset_time}")
        if candles:
            df = pd.DataFrame(candles, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')

            all_data = pd.concat([all_data, df], ignore_index=True)

            # Update start_date for the next batch
            start_date = df['Date'].max() + pd.Timedelta(seconds=1)
        else:
            # No more data available
            break

    # print(all_data.iloc[2]['Date'])
    all_data['Date'] = pd.to_datetime(all_data['Date'], unit='ms')
    # print(type(all_data.iloc[2]['Date']))

    all_data['Date'] = all_data['Date'].dt.tz_localize(pytz.UTC).dt.tz_convert(target_timezone)
    

    all_data['Date'] = pd.to_datetime(all_data['Date']).dt.tz_localize(None)

    # print(type(all_data.iloc[0]['Date']))
 
    output_folder = './months/' + symbol + '/'
    csv_file = f'{output_folder}/{symbol}-{timeframe}.csv'
    if not os.path.exists(csv_file):
        all_data.to_csv(csv_file, index=False)
    else:
        # Append the data to the existing CSV file
        all_data.to_csv(csv_file, mode='a', header=False, index=False)

    # all_data.to_csv(csv_file, index=False)

# pair = symbol
#TODO check if file exists if not make it
def checkIfUpToDate(pair, timeframe):
    now = datetime.now()

    filePath = './months/' + pair + '/' + pair + '-' + timeframe + '.csv'

    if not os.path.exists(filePath):
        emptyDf = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        emptyDf.to_csv(filePath, index=False)

    pairDf = pd.read_csv(filePath)

    if not len(pairDf) == 0:

        lastOfPair = pairDf.iloc[-1]['Date']

        lastOfPair = pd.to_datetime(lastOfPair)
    else:
        return False
    # print(lastOfPair)
    # print(now)

    if timeframe == '1m':
        return now.minute == lastOfPair.minute
    elif timeframe == '1h':
        return now.hour == lastOfPair.hour
    elif timeframe == '1d':
        return now.day == lastOfPair.day
    elif timeframe == '1w':
        # Get year and week number for current datetime
        current_year, current_week, _ = now.isocalendar()
        # Get year and week number for the lastOfPair datetime
        last_year, last_week, _ = lastOfPair.isocalendar()

        return current_week == last_week
    else:
        return False
    
# if 
def returnLastDate(pair, timeframe):

    # Get the current time
    current_time = datetime.now()

    # Define a dictionary to map timeframes to timedelta units
    timeframe_to_timedelta = {
        '1m': timedelta(minutes=1),
        '1h': timedelta(hours=1),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
    }

    timeframe_delta = timeframe_to_timedelta.get(timeframe)


    numOfCandles = candlesToLoad.get(timeframe)

    time_to_go_back = numOfCandles * timeframe_delta
    target_date = current_time - time_to_go_back
    target_date_str = target_date.strftime('%Y-%m-%d %H:%M:%S')


    pairDf = pd.read_csv('./months/' + pair + '/' + pair + '-' + timeframe + '.csv')
    
    if not len(pairDf) == 0:
        lastOfPair = pairDf.iloc[-1]['Date']
        print("lastOfPair", lastOfPair, " ", pair, " ", timeframe)
    else:
        return target_date_str

    return lastOfPair



def handleDataLoading(pair, timeframe):
    if checkIfUpToDate(pair, timeframe):
        print("Data is up to date", pair, timeframe)
    else:
        print("Updating data", pair, timeframe)
        download_historical_data(returnLastDate(pair, timeframe), pair, timeframe)

    updateData(pair, timeframe)



# print(checkIfUpToDate('BTCBUSD', '1h'))



# To keep the data up to date by downloading new data every period and specify the location:
def updateData(pair, timeframe):

    pairDf = pd.read_csv('./months/' + pair + '/' + pair + '-' + timeframe + '.csv')
    lastOfPair = pairDf.iloc[-1]['Date']
    lastOfPair = pd.to_datetime(lastOfPair)
    # lastOfPair = pd.to_datetime(lastOfPair, unit='ms', origin='unix', utc=True)
    latest_timestamp = lastOfPair # Initialize the latest timestamp as None

    while True:
        # print("...")
        # translation to binance format, cannot be asigned to the same variable 
        # because it is later reused so it hs to be unchanged
        pairBinance = symbolTranslation.get(pair)
        latest_candle = binance.fetch_ohlcv(pairBinance, timeframe, limit=1)
        if latest_candle:
            timestamp = latest_candle[0][0]
            timestamp = pd.to_datetime(timestamp, unit='ms')
            timestamp = timestamp.tz_localize(pytz.UTC).tz_convert(target_timezone)
            timestamp = pd.to_datetime(timestamp).tz_localize(None)        


            if timestamp != latest_timestamp:
                latest_timestamp = timestamp  

                df = pd.DataFrame(latest_candle, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['Date'] = pd.to_datetime(df['Date'], unit='ms')
                df['Date'] = df['Date'].dt.tz_localize(pytz.UTC).dt.tz_convert(target_timezone)
                df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

                # Specify the location where you want to save the updated data
                output_folder = './months/' + pair + '/'
                csv_file = f'{output_folder}BTCBUSD-{timeframe}.csv'

                # df.to_csv(csv_file, mode='a', header=False, index=False)

        time.sleep(1)  # 1 second

# before or after date, diretion suggests if it is before or after
def findDateNCandlesBeforeDate(timeframe, date, candlesToLoad, direction):

    timeframe_to_timedelta = {
        '1m': timedelta(minutes=1),
        '1h': timedelta(hours=1),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
    }

    timeframe_delta = timeframe_to_timedelta.get(timeframe)
    
    timeToLoad = candlesToLoad * timeframe_delta
    if direction == '<':
        target_date = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S') - timeToLoad
    elif direction == '>':
        target_date = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S') + timeToLoad

    target_date = target_date.strftime('%Y-%m-%d %H:%M:%S')

    return target_date






def create_data_folders_and_files(app_data, root_folder='./months'):
    symbols = app_data['symbols']
    timeframes = app_data['timeframes']

    # Create the root folder if it doesn't exist
    os.makedirs(root_folder, exist_ok=True)



    # Create subfolders for each symbol
    for symbol in symbols:
        symbol_folder = os.path.join(root_folder, symbol)
        os.makedirs(symbol_folder, exist_ok=True)

        # Create files for each timeframe inside the symbol folder
        for timeframe in timeframes:
            # print(symbol, timeframe)

            filename = f'{symbol}-{timeframe}.csv'
            file_path = os.path.join(symbol_folder, filename)
            # Create an empty CSV file with column names if it doesn't exist
            if not os.path.exists(file_path):
                df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df.to_csv(file_path, index=False)

# function to load data for all pairs and timeframes
def handleLoadingOfAllPairsAndTimeframes(app_data):
    symbols = app_data['symbols']
    timeframes = app_data['timeframes']

    # Create and start a thread for each pair and timeframe
    threads = []
    for symbol in symbols:
        for timeframe in timeframes:
            # print(symbol, " || " ,timeframe)
            thread = threading.Thread(target=handleDataLoading, args=(symbol, timeframe))
            # thread.setDaemon(True)
            threads.append(thread)
            thread.start()

def isSymbolListedOnBinance(symbol):
    exchange = ccxt.binance()

    # Get the list of trading pairs (symbols) on Binance
    exchange_symbols = exchange.load_markets()

# Check if the symbol exists in the list of trading pairs
    if symbol in exchange_symbols:
        # print(f"{symbol} is listed on Binance.")
        return True
    else:
        return False
        # print(f"{symbol} is not listed on Binance.")



create_data_folders_and_files(app_data)

# handleLoadingOfAllPairsAndTimeframes(app_data)


# # Fetch the list of trading pairs (symbols)
# all_pairs = exchange.load_markets()

# # Extract the trading pairs from the loaded markets
# available_pairs = list(all_pairs.keys())

# # Print the available trading pairs
# for pair in available_pairs:
#     print(pair)

