from operator import rshift
import time
import pyupbit
import sys
import talib
import numpy as np
import subprocess
import datetime

#--mock_investment--
class Mock_investment:
    def __init__(self, budget):
        self.mock_budget = budget  #KRW
        self.mock_BTC = 0  #BTC
    def get_balances(self, ticker):
        return self.mock_budget
    def buy_market_order(self):
        pass
    def sell_market_order(self):
        pass
# ----------------------------------------------------------------
mock_flag = 0;
if mock_flag ==1:
    mock_investment = Mock_investment(10000000)
f = open("access.txt", 'r', encoding='utf-8')
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()
confirm = input("Run Auto Trading? (y/n): ")
if confirm == "y":
    upbit = pyupbit.Upbit(access, secret)
    print("Login Sccess!!")
else:
    sys.exit("Program exit.")
logger = subprocess.Popen('python logger.py', creationflags = subprocess.CREATE_NEW_CONSOLE, stdin = subprocess.PIPE)
print("Autotrading Start...\n")
# -----------------------------------------------------------------

def get_balance(ticker, mock_flag):
    if (mock_flag==1):
        return mock_investment.get_balances(ticker);
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                logger.stdin.write(f"{'Finding Buy signal..' if ticker == 'KRW' else 'Finding Sell signal..'}  Balance: {float(b['balance'])}{ticker}  [{datetime.datetime.now().strftime('%H:%M:%S')}]\n".encode('utf-8'))
                logger.stdin.flush()
                return float(b['balance'])
            else:
                return 0

def buy_order(ticker, volume, mock_flag):
    try:
        while True:
            if mock_flag ==1:
                buy_result = mock_investment.buy_market_order()
            else:
                buy_result = upbit.buy_market_order(ticker, volume)
            if buy_result == None or 'error' in buy_result:
                print("매수 재 주문")
                time.sleep(1)
            else:
                return buy_result
    except:
        print("매수 주문 이상")


def sell_order(ticker, volume, mock_flag):
    try:
        while True:
            if mock_flag==1:
                sell_result = upbit.sell_market_order();
            else:
                sell_result = upbit.sell_market_order(ticker, volume)
            if sell_result == None or 'error' in sell_result:
                print("매도 재 주문")
                time.sleep(1)
            else:
                return sell_result
    except:
        print("매도 주문 이상")

  
def log(_dict, mock_flag):
    diction = {"bid": "매수주문", "ask": "매도주문"}
    _created_at = _dict['created_at'][:10] + " " + _dict['created_at'][11:19]
    print("!!모의거래!!" if (mock_flag==1) else "")
    print(f"[{_created_at}] {_dict['market']} {diction[_dict['side']]} ({_dict['locked']})")


class Indicator:
    def __init__(self,ticker,_interval,_count):
        self.df = pyupbit.get_ohlcv(ticker, interval=_interval, count=_count)

    def now_rsi(self):
        rsi = talib.RSI(np.asarray(self.df['close']), 14)
        return rsi[-1]

    def now_macdOR(self):
        hist = talib.MACD(np.asarray(self.df['close']), fastperiod=8, slowperiod=21, signalperiod=5)[2][-1]
        return hist

    def now_stochastic(self):
        slowk, slowd = talib.STOCH(np.asarray(self.df['high']), np.asarray(self.df['low']), np.asarray(self.df['close']), fastk_period=14, slowk_period=3, slowd_period=3)
        return [slowk[-1], slowd[-1]]

def bid_check():  #매수조건
    indicator = Indicator("KRW-BTC", "minute1", 200)
    stc = indicator.now_stochastic()
    rs = indicator.now_rsi()
    maOR = indicator.now_macdOR()
    logger.stdin.write(f" - stochastic: {stc[0]}, {stc[1]} rsi: {rs} macdOR: {maOR}\n".encode('utf-8'))
    logger.stdin.flush()
    cnt = True
    cnt = cnt and (True if stc[0] < 80 and stc[1] < 80 else False)
    cnt = cnt and (True if rs >= 50 else False)
    cnt = cnt and (True if maOR >= 0 else False)
    return cnt

def ask_check(): # 매도조건
    indicator = Indicator("KRW-BTC", "minute1", 200)
    stc = indicator.now_stochastic()
    rs = indicator.now_rsi()
    maOR = indicator.now_macdOR()
    logger.stdin.write(f" - stochastic: {stc[0]}, {stc[1]} rsi: {rs} macdOR: {maOR}\n".encode('utf-8'))
    logger.stdin.flush()
    cnt = 0
    cnt += 1 if stc[0] >= 80 and stc[1] >= 80 else 0
    cnt += 1 if rs <= 50 else 0
    cnt += 1 if maOR <= 0 else 0
    if cnt >= 2:
        return True
    else:
        return False

while True:
    try:
        while True:
            if get_balance("KRW", mock_flag) > 5000:
                if bid_check():
                    log(buy_order("KRW-BTC", get_balance("KRW", mock_flag)*0.9995, mock_flag), mock_flag)
                    time.sleep(1)
                    break
                time.sleep(0.5)
            else:
                break

            time.sleep(0.5)

        while True:
            if get_balance("BTC", mock_flag) > 0.00008:
                if ask_check():
                    log(sell_order("KRW-BTC", get_balance("BTC", mock_flag)*0.9995, mock_flag), mock_flag)
                    time.sleep(1)
                    break
                time.sleep(0.5)
            else:
                break

            time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)
        pass
