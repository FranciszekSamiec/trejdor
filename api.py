from libraries import * 


def parseSymbol(symbol):
    new_symbol = symbol.replace('/', '')
    return new_symbol


binance = ccxt.binance({
    'rateLimit': 1200,  # Adjust the rate limit as needed
})

target_timezone = pytz.timezone("EUROPE/Warsaw")

all_data = pd.DataFrame()


symbol = 'BTC/BUSD'  # Example trading pair (Bitcoin/USDT)
symbol = parseSymbol(symbol)  # Update the symbol here

timeframe = '1h'    # Example timeframe (1 hour candles)


def download_historical_data(startDate):
    # start_date = pd.to_datetime("2023-01-01 00:00:00")
    start_date = pd.to_datetime(startDate)
    end_date = datetime.now()
    all_data = pd.DataFrame()

    while start_date <= end_date:
        since = int(start_date.timestamp() * 1000)
        until = int(end_date.timestamp() * 1000)
    

        candles = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
   

        if candles:
            df = pd.DataFrame(candles, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')

            all_data = pd.concat([all_data, df], ignore_index=True)

            # Update start_date for the next batch
            start_date = df['Date'].max() + pd.Timedelta(seconds=1)
        else:
            # No more data available
            break

    print(all_data.iloc[2]['Date'])
    all_data['Date'] = pd.to_datetime(all_data['Date'], unit='ms')
    print(type(all_data.iloc[2]['Date']))

    all_data['Date'] = all_data['Date'].dt.tz_localize(pytz.UTC).dt.tz_convert(target_timezone)
    
    # for column in df.iloc[:, 1:]:
    #     all_data[column] = all_data[column].astype(int)
    all_data['Date'] = pd.to_datetime(all_data['Date']).dt.tz_localize(None)



    print(type(all_data.iloc[0]['Date']))
    # print(type(data.iloc[0]['High']))
    # print(type(data.iloc[0]['Low']))

    # Group the data by month
    monthly_data = all_data.groupby(all_data['Date'].dt.strftime('%Y-%m'))

    # Specify the location where you want to save the historical data
    output_folder = './months/' + symbol + '/'

    # Save each monthly group to a separate CSV file
    for month, data in monthly_data:
        
        csv_file = f'{output_folder}BTCBUSD-1h-{month}.csv'
        # Assuming your DataFrame is named df
        data = data.iloc[1:]
        data.to_csv(csv_file, index=False)


# def checkIfUpToDate(pair):






# To keep the data up to date by downloading new data every second and specify the location:
# def update_one_minute_data():
#     while True:
#         latest_candle = binance.fetch_ohlcv(symbol, timeframe, limit=1)

#         if latest_candle:
#             df = pd.DataFrame(latest_candle, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#             df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

#             # Specify the location where you want to save the updated data
#             file_path = './months/binance_one_second_historical_candles.csv'
#             df.to_csv(file_path, mode='a', header=False, index=False)

#         time.sleep(1)  # 1 second

download_historical_data("2020-01-01 00:00:00")

# update_one_minute_data()