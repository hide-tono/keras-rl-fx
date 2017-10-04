import datetime
import os

import numpy
import pandas
from dateutil import relativedelta

now = datetime.datetime.now()
csv_file_paths = []
for _ in range(4):
    now = now - relativedelta.relativedelta(months=1)
    filename = 'DAT_MT_EURUSD_M1_{}.csv'.format(now.strftime('%Y%m'))
    if not os.path.exists(filename):
        print('ファイルが存在していません。下記からダウンロードしてください。', filename)
        print('http://www.histdata.com/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/EURUSD/')
    else:
        csv_file_paths.append(filename)

data = pandas.DataFrame()
read_index = 0
for path in csv_file_paths:
    csv = pandas.read_csv(path,
                          names=['date', 'time', 'open', 'high', 'low', 'close', 'v'],
                          parse_dates={'datetime': ['date', 'time']},
                          )
    csv.index = csv['datetime']
    csv = csv.drop('datetime', axis=1)
    csv = csv.drop('v', axis=1)
    data = data.append(csv)
    # 最後に読んだCSVのインデックスを開始インデックスとする
    read_index = len(data) - len(csv)

visible_bar = 64
target = data.iloc[read_index - 60 * 4 * 70: read_index]

m1 = numpy.array(target.iloc[-1 * visible_bar:][target.columns])
m5 = numpy.array(target.resample('5min').agg({'open': 'first',
                                              'high': 'max',
                                              'low': 'min',
                                              'close': 'last'}).dropna().iloc[-1 * visible_bar:][target.columns])
m30 = numpy.array(target.resample('30min').agg({'open': 'first',
                                                'high': 'max',
                                                'low': 'min',
                                                'close': 'last'}).dropna().iloc[-1 * visible_bar:][target.columns])
h4 = numpy.array(target.resample('4H').agg({'open': 'first',
                                            'high': 'max',
                                            'low': 'min',
                                            'close': 'last'}).dropna().iloc[-1 * visible_bar:][target.columns])
result = numpy.array([m1, m5, m30, h4])

print(result.shape)

