# coding=utf-8
import gym
import numpy
import pandas
from gym import spaces


class FxEnv(gym.Env):
    metadata = {'render.modes': ['human', 'ohlc_array']}

    def __init__(self, csv_path):
        # 定数
        self.STAY = 0
        self.BUY = 1
        self.SELL = 2
        self.CLOSE = 3
        # 対象となる通貨ペアの最大値
        self.MAX_VALUE = 2
        # 初期の口座資金
        self.initial_balance = 10000
        # CSVファイルのパス
        self.csv_file_path = csv_path
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
        # 1分足、5分足、30分足、4時間足、日足の5時系列データを64本分
        self.observation_space = spaces.Box(low=0, high=self.MAX_VALUE, shape=numpy.shape([5, 64, 4]))

    def _reset(self):
        self.info = AccountInformation(self.initial_balance)
        # CSVを読み込む
        self.data = pandas.read_csv(self.csv_file_path,
                                    names=['date', 'time', 'o', 'h', 'l', 'c', 'v'],
                                    parse_dates={'datetime': ['date', 'time']},
                                    )
        # CSVのインデックス
        self.read_index = 0
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
                        self.total_pips += profit
                        self.total_pips_buy += profit
                    elif ticket.order_type == self.SELL:
                        # 売りチケットをクローズ
                        profit = (ticket.open_price - ask) * ticket.lots
                        self.total_pips += profit
                        self.total_pips_sell += profit

        # インデックスをインクリメント
        self.read_index += 1
        # obs, reward, done, infoを返す TODO infoを作る
        return self.make_obs(), self.obs.balance, self.read_index >= len(self.data), self.info

    def _render(self, mode='human', close=False):
        if mode == 'human':
            return self.balance
        else:
            pass

    def make_obs(self):
        """
        1分足、5分足、30分足、4時間足、日足の5時系列データを64本分作成する
        :return:
        """
        if self._obs_type == 'human':
            # humanの場合はmatplotlibでチャートのimgを作成する
            pass
        elif self._obs_type == 'ohlc_array':
            # TODO
            return


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
