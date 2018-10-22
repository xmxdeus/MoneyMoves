import plotly as py
import plotly.graph_objs as go
import time
import datetime
import pandas as pd
import csv
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#import fecon236 as fe


#Setting up access keys
from binance.client import Client
me = Client('8SAIJoi16tUuUl3TN5QfwNMbD9gt7vDXl00LDBsC7cCsVOePJH3vgxNMAU8oEJu3', 'zBWMmcRT945jBEoTlKz7BFyNdPWpd05MaQiL17LUeOhR2SC5CAKVS5gIn8CwBEPT')

#interval_to_milliseconds
def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds
    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str
    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms

#retrieve yearly dataset from Binance
def get_historical_klines(symbol, interval):
    """Get Historical Klines from Binance
    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/
    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str
    :return: list of OHLCV values
    """

    # create the Binance client, no need for api key
    client = Client("", "")

    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    start_ts = 1499644800000 #10th Jul 2017 01:00:00

    end_ts = None

    idx = 0

    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data
end2 = 0

#choice of intervals:Client.KLINE_INTERVAL_2HOUR
#'ETHBTC'
def download_dataset(symbol, interval):

    end = int(round(time.time() * 1000))
    end2 = end
    interval = interval

    klines=get_historical_klines(symbol, interval)

    start = 1499644800000


# uncomment to convert milliseconds to datetime
    for i in range(len(klines)):
        klines[i][0]=datetime.datetime.fromtimestamp(klines[i][0]/1000.0)

    data_label = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'NumOfTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'Ignore']
    klines.insert(0, data_label)

    filename = "/Users/Amduz/Documents/7r4d1ng/PatternRecognition/Binance_{}_{}_{}-{}.csv".format(
        symbol,
        interval,
        start,
        end
    )
    with open(filename,
        'wb'
    ) as fp:
        writer=csv.writer(fp)
        writer.writerows(klines)

    return filename


#draw line graph
def draw_linegraph(filename):

    gf = pd.read_csv("/Users/Amduz/Documents/7r4d1ng/PatternRecognition/"+filename)


    gf.Open.plot(color='black')#the changes matter not the position, by how much each point moves
    gf.High.plot(color='green')
    gf.Low.plot(color='red')
    gf.Volume.plot.bar(secondary_y=True, grid=True, color='purple')
    plt.show()

# # plotly
#     trace_high = go.Scatter(
#         x=gf.Time,
#         y=gf['High'],
#         name = "ETH High",
#         line = dict(color = '#17BECF'),
#         opacity = 0.8)
#
#     trace_low = go.Scatter(
#         x=gf.Time,
#         y=gf['Low'],
#         name = "ETH Low",
#         line = dict(color = '#7F7F7F'),
#         opacity = 0.8)
#
#     trace_open = go.Scatter(
#         x=gf.Time,
#         y=gf.Open,
#         name='ETH Open',
#         line = dict(color='#234152'),
#         opacity = 0.8)
#
#     trace_volume = go.Bar(
#         x=gf.Time,
#         y=gf.Volume,
#         name='ETH Volume',
#         yaxis='y2',
#         marker=dict(color='rgb(158,202,225)')
#         )
#
#     data = [trace_high,trace_low, trace_open, trace_volume]
#
#     layout = dict(
#         title=filename[:18] + ' with Rangeslider',
#         yaxis=dict(
#             title='BTC per ETH'),
#         yaxis2=dict(
#             title='Volume',
#             titlefont=dict(color='rgb(148,103,189)'),
#             tickfont=dict(color='rgb(148,103,189)'),
#             overlaying='y',
#             side='right'),
#         xaxis=dict(
#             rangeselector=dict(
#                 buttons=list([
#                     dict(count=1,
#                          label='1h',
#                          step='hour',
#                          stepmode='backward'),
#                     dict(count=2,
#                          label='2h',
#                          step='hour',
#                          stepmode='backward'),
#                     dict(count=4,
#                          label='4h',
#                          step='hour',
#                          stepmode='backward'),
#                     dict(count=6,
#                          label='6h',
#                          step='hour',
#                          stepmode='backward'),
#                     dict(count=12,
#                          label='12h',
#                          step='hour',
#                          stepmode='backward'),
#                     dict(count=1,
#                          label='1d',
#                          step='day',
#                          stepmode='backward'),
#                     dict(count=7,
#                          label='1w',
#                          step='day',
#                          stepmode='backward'),
#                     dict(step='all')
#                 ])
#             ),
#             rangeslider=dict(),
#             type='date'
#         )
#     )
#
#     fig = dict(data=data, layout=layout)
#     # py.offline.plot(fig, filename = filename[:18]+".html")

#OHLC chart
def draw_OHLCgraph(filename):

    gf = pd.read_csv("/Users/Amduz/Documents/7r4d1ng/PatternRecognition/"+filename)

    traceOHLC = go.Ohlc( x = gf.Time,
                         open = gf.Open,
                         high = gf.High,
                         low = gf.Low,
                         close = gf.Close)
    dataOHLC = [traceOHLC]
    layoutOHLC = dict(
        title=filename[:18] + ' OHLC with Rangeslider',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=2,
                         label='2h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=4,
                         label='4h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=6,
                         label='6h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=12,
                         label='12h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=1,
                         label='1d',
                         step='day',
                         stepmode='backward'),
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='date'
            )
        )

    figOHLC = dict(data=dataOHLC, layout=layoutOHLC)
    # py.offline.plot(figOHLC, filename = filename[:18]+".html")

def calculate_differences(filename):

    gf = pd.read_csv("/Users/Amduz/Documents/7r4d1ng/PatternRecognition/"+filename)


    trace_high = go.Scatter(
        x=gf.Time,
        y=gf['High'],
        name = "ETH High",
        line = dict(color = '#17BECF'),
        opacity = 0.8)

    trace_low = go.Scatter(
        x=gf.Time,
        y=gf['Low'],
        name = "ETH Low",
        line = dict(color = '#7F7F7F'),
        opacity = 0.8)

    trace_open = go.Scatter(
        x=gf.Time,
        y=gf.Open,
        name='ETH Open',
        line = dict(color='#234152'),
        opacity = 0.8)

    trace_bull = go.Scatter(
        x=gf.Time,
        y=gf['High']-gf['Open'],
        name = "ETH Bull Index",
        yaxis='y2',
        line = dict(color = '#17BEED'),
        opacity = 0.8)

    trace_bear = go.Scatter(
        x=gf.Time,
        y=gf['Open']-gf['Low'],
        name = "ETH Bear Index",
        yaxis='y2',
        line = dict(color = '#7F7FAC'),
        opacity = 0.8)

    data = [trace_bull, trace_bear,trace_high,trace_low, trace_open]

    layout = dict(
        title='Diff_'+filename[:18] + ' no Volume',
        yaxis=dict(
            title='BTC per ETH'),
        yaxis2=dict(
            title='Index',
            titlefont=dict(color='rgb(148,103,189)'),
            tickfont=dict(color='rgb(148,103,189)'),
            overlaying='y',
            side='right'),
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=2,
                         label='2h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=4,
                         label='4h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=6,
                         label='6h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=12,
                         label='12h',
                         step='hour',
                         stepmode='backward'),
                    dict(count=1,
                         label='1d',
                         step='day',
                         stepmode='backward'),
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(),
            type='date'
        )
    )

    fig = dict(data=data, layout=layout)
    # py.offline.plot(fig, filename = 'Diff_'+filename[:18]+".html")

# new_file = download_dataset('ETHBTC', Client.KLINE_INTERVAL_12HOUR)
draw_linegraph('Binance_ETHBTC_12h_1499644800000-1532827207767.csv')
# draw_linegraph('')
# calculate_differences('')


##TESORFLOW----------------



import tensorflow as tf

##a = tf.constant(3.0)
##b = tf.constant(4.0)
##total = a + b

##writer = tf.summary.FileWriter('.')
##writer.add_graph(tf.get_default_graph())
#tensorboard --logdir=[path]
#localhost:6006 for tensorboard

# sess = tf.Session()

##print(sess.run({'ab':(a, b), 'total':total}))

#single value during run
##vec = tf.random_uniform(shape=(3,))
##out1 = vec + 1
##out2 = vec + 2
##print(sess.run(vec))
##print(sess.run(vec))
##print(sess.run((out1, out2)))

#a promise to provide value later (like a function argument)
# x = tf.placeholder(tf.float32)
# y = tf.placeholder(tf.float32)
# z = x + y

# print(sess.run(z, feed_dict={x: 3, y: 4.5}))
# print(sess.run(z, feed_dict={x: [1, 3], y: [2, 4]}))


def 
