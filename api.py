from libraries import * 





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

    

    start_date = datetime.strptime(startDate, '%Y-%m-%d %H:%M:%S')

    # start_date = start_date - timedelta(hours=1)
    
    print(start_date)
    start_date = start_date.astimezone(pytz.UTC)
    start_date = start_date.astimezone(pytz.UTC).replace(tzinfo=None)

    print(start_date)


    # start_date = pd.to_datetime(startDate)
    end_date = datetime.now()
    all_data = pd.DataFrame()

    while start_date <= end_date:
        since = int(start_date.timestamp() * 1000)
        until = int(end_date.timestamp() * 1000)
    

        candles = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        print(candles)

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
    csv_file = f'{output_folder}BTCBUSD-{timeframe}.csv'
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
    print(len(pairDf))
    if not len(pairDf) == 0:
        print("kurwa")

        lastOfPair = pairDf.iloc[-1]['Date']
        print("kurwa")

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
        return now.week == lastOfPair.week
    elif timeframe == '1M':
        return now.month == lastOfPair.month
    else:
        print("Wrong timeframe")
        return False
    
def returnLastDate(pair, timeframe):
    global ultimateBeginDate

    candlesToLoad = 26000
    # Get the current time
    current_time = datetime.now()

    # Define a dictionary to map timeframes to timedelta units
    timeframe_to_timedelta = {
        '1m': timedelta(minutes=1),
        '1h': timedelta(hours=1),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
        '1M': timedelta(days=30)  # Approximation for a month
    }

    timeframe_delta = timeframe_to_timedelta.get(timeframe)

    time_to_go_back = candlesToLoad * timeframe_delta
    target_date = current_time - time_to_go_back
    target_date_str = target_date.strftime('%Y-%m-%d %H:%M:%S')



    pairDf = pd.read_csv('./months/' + pair + '/' + pair + '-' + timeframe + '.csv')
    
    if not len(pairDf) == 0:
        lastOfPair = pairDf.iloc[-1]['Date']
    else:
        return target_date_str

    return lastOfPair



def handleDataLoading(pair, timeframe):
    if checkIfUpToDate(pair, timeframe):
        print("Data is up to date")
    else:
        print("Updating data")
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
    print("****")
    print(latest_timestamp)

    while True:
        print("beep beep...")
        latest_candle = binance.fetch_ohlcv(pair, timeframe, limit=1)
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

                df.to_csv(csv_file, mode='a', header=False, index=False)

        time.sleep(1)  # 1 second

# download_historical_data("2023-01-01 00:00:00", "BTCBUSD", "1h")


handleDataLoading('BTCBUSD', '1m')

# download_historical_data("2023-09-26 00:00:00", "BTCBUSD", "1m")

# update_one_minute_data()