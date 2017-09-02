# coding=utf-8
import gym
import numpy
import pandas
from gym import spaces
import matplotlib.pyplot as plt
import matplotlib.finance as mpf


class FxEnv(gym.Env):
    metadata = {'render.modes': ['human', 'ohlc_array']}

    def __init__(self, csv_paths):
        # 定数
        self.STAY = 0
        self.BUY = 1
        self.SELL = 2
        self.CLOSE = 3
        # 対象となる通貨ペアの最大値
        self.MAX_VALUE = 2
        # 初期の口座資金
        self.initial_balance = 10000
        # CSVファイルのパス配列(最低4ヶ月分を昇順で)
        self.csv_file_paths = csv_paths
        # スプレッド
        self.spread = 0.5
        # Point(1pipsの値)
        self.point = 0.0001
        # 利食いpips
        self.take_profit_pips = 30
        # 損切りpips
        self.stop_loss_pips = 15
        # ロット数
        self.lots = 0.1
        # 1分足、5分足、30分足、4時間足の5時系列データを64本分作る
        self.observation_space = spaces.Box(low=0, high=self.MAX_VALUE, shape=numpy.shape([4, 64, 4]))

    def _reset(self):
        self.info = AccountInformation(self.initial_balance)
        # CSVを読み込む
        self.data = pandas.DataFrame()
        for path in self.csv_file_paths:
            csv = pandas.read_csv(self.csv_file_path,
                                  names=['date', 'time', 'open', 'high', 'low', 'close', 'v'],
                                  parse_dates={'datetime': ['date', 'time']},
                                  )
            csv.index = csv['datetime']
            csv = csv.drop('datetime', axis=1)
            csv = csv.drop('v', axis=1)
            self.data = csv.append(csv)
            # 最後に読んだCSVのインデックスを開始インデックスとする
            self.read_index = len(self.data) - len(csv)
            # チケット一覧
        self.tickets = []

    def _step(self, action):
        current_data = self.data.iloc[self.read_index]
        ask = current_data['c'] + self.spread * self.point
        bid = current_data['c'] - self.spread * self.point

        if action == self.STAY:
            # TODO stay
            pass
        elif action == self.BUY:
            ticket = Ticket(self.BUY, ask, ask + self.take_profit_pips * self.point,
                            ask - self.stop_loss_pips * self.point, self.lots)
            self.tickets.append(ticket)
            pass
        elif action == self.SELL:
            ticket = Ticket(self.SELL, bid, bid - self.take_profit_pips * self.point,
                            bid + self.stop_loss_pips * self.point, self.lots)
            self.tickets.append(ticket)
            pass
        elif action == self.CLOSE:
            if len(self.tickets) > 0:
                for i in range(len(self.tickets)):
                    ticket = self.tickets[i]
                    if ticket.order_type == self.BUY:
                        # 買いチケットをクローズ
                        profit = (bid - ticket.open_price) * ticket.lots
                        self.info.total_pips += profit
                        self.info.total_pips_buy += profit
                    elif ticket.order_type == self.SELL:
                        # 売りチケットをクローズ
                        profit = (ticket.open_price - ask) * ticket.lots
                        self.info.total_pips += profit
                        self.info.total_pips_sell += profit

        # インデックスをインクリメント
        self.read_index += 1
        # obs, reward, done, infoを返す
        return self.make_obs(), self.obs.balance, self.read_index >= len(self.data), self.info

    def _render(self, mode='human', close=False):
        if mode == 'human':
            return self.balance
        else:
            pass

    def make_obs(self):
        """
        1分足、5分足、30分足、4時間足の4時系列データを64本分作成する
        :return:
        """
        target = self.data.iloc[self.read_index - 60 * 4 * 70: self.read_index]
        if self._obs_type == 'human':
            # humanの場合はmatplotlibでチャートのimgを作成する?
            plt.figure(figsize=(10, 4))
            ax = plt.subplot(2, 2, 1)
            # y軸のオフセット表示を無効にする。
            ax.get_yaxis().get_major_formatter().set_useOffset(False)
            data = target.iloc[-64:].values
            # ローソク足は全横幅の太さが1である。表示する足数で割ってさらにその1/3の太さにする
            width = 1.0 / 64 / 3
            mpf.candlestick_ohlc(ax, data, width=width, colorup='g', colordown='r')

            pass
        elif self._obs_type == 'ohlc_array':
            # TODO これだとcloseしか利用していないので正確ではない
            m1 = numpy.array(target.iloc[-64:][target.columns])
            m5 = numpy.array(target['close'].resample('5min').ohlc().dropna().iloc[-64:][target.columns])
            m30 = numpy.array(target['close'].resample('30min').ohlc().dropna().iloc[-64:][target.columns])
            h4 = numpy.array(target['close'].resample('4H').ohlc().dropna().iloc[-64:][target.columns])
            return numpy.array([m1, m5, m30, h4])


class AccountInformation(object):
    """
    口座情報クラス
    """

    def __init__(self, initial_balance):
        # 口座資金
        self.balance = initial_balance
        # 総獲得pips
        self.total_pips = 0
        # 総獲得pips(買い)
        self.total_pips_buy = 0
        # 総獲得pips(売り)
        self.total_pips_sell = 0
        # チャート
        self.chart = []


class Ticket(object):
    """
    チケット
    """

    def __init__(self, order_type, open_price, take_profit, stop_loss, lots):
        # タイプ
        self.order_type = order_type
        # 約定価格
        self.open_price = open_price
        # 利食い価格
        self.take_profit = take_profit
        # 損切り価格
        self.stop_loss = stop_loss
        # ロット
        self.lots = lots
