#  Treydor  📈💹

Welcome to the Treydor App repository! This is a Python Dash application that allows users to manually open long and short positions and instantly visualizes the results on the equity chart. It's a powerful tool for traders to experiment with different strategies and gain insights into their trades.

## Table of Contents

- [`Features`](#features)
- [`Getting Started`](#getting-started)
- [`Usage`](#usage)
- [`Roadmap`](#roadmap)
- [`Contributing`](#contributing)
- [`License`](#license)


## `Features` 📋

- 📊 Real-time Equity Chart: Visualize the impact of your trading decisions in real-time.
- 📈 Manual Position Management: Open and manage long and short positions with ease.
- 🔄 Interactive Dashboards: User-friendly interface for a seamless trading experience.

## `Getting Started` 🚦

1. Clone this repository to your local machine:


2. Install the required dependencies: ``` pip install dash ```, ```pip install plotly```


3. Run the app


4. Access the app in your web browser at [http://localhost:8050](http://localhost:8050).

## `Usage` 📖

![Screenshot 2023-10-17 at 17 27 42](https://github.com/FranciszekSamiec/trejdor/assets/49732831/accdc9d5-5791-4cf3-b17d-b07ae565c9a9)
1. This is the symbol and timeframe menu. Here you can also add or delete symbols from the app's menuu. Symbols are downloaded from binance exchange. this allows user tocontrol memory usage of ohlc data.
2. Indicator menu depicts indicators that are currently added to the chart. Tt allows user to switch them on/off. Later comprehensive indicator base will be added.
3. vertical loader line allows user to load/hide data. Annotation on the bottom says how many candles user wants to hide/load. User can set this number by clicking on the annotation and changing the number. If the data is loaded up to the present, it will be indicated by the vertical dashed line with only one arrow pointing left.
4. This is the control panel, it allows user to:
   - set specific date range to depict,
   - choose direction of the position to be set,
   - enter the percent willing to risk at each trade,
   - set start capital,
   - reset all trading history,
5. This is equity chart, it depicts history of the equity and drawdown as a blue histogram attached to ceiling. 

User can set open position by simply clicking on the candle at which he wants to enter the market. User can click and drag the odges of the position rectangle and app will automatically adjust equity chart to changes in long/short position. 
   
## `Roadmap` 🛣️

Here's what we have in store for the future of the Trading App:

- 🚀 Deployment with Heroku: Make the app accessible online.
- 📈 Advanced ML Features: Implement econometric models like ARIMA, SARIMA for forecasting.
- 📊 More Indicators: Expand the set of technical indicators for analysis.
- 🌐 Multiple Exchanges: Extend the app's support to different cryptocurrency markets.
- 💡 Make app more respnsive by using javascript.


## `License` 📜

This project is licensed under the MIT License. See the [`LICENSE`](LICENSE) file for details.

Happy Trading! 📈💰
