import time
import pyupbit
import sys
import talib
import numpy as np
import subprocess
import datetime

# ----------------------------------------------------------------
f = open("access.txt", 'r')
lines = f.readlines()
access = lines[0].strip()
secret = lines[1].strip()
f.close()
confirm = input("Do you want to run Auto Trading? (y/n): ")
if confirm == "y":
    upbit = pyupbit.Upbit(access, secret)
    print("Login Sccess!!")
else:
    sys.exit("Program exit.")
logger = subprocess.Popen('python logger.py', creationflags = subprocess.CREATE_NEW_CONSOLE, stdin = subprocess.PIPE)
print("Autotrading Start...\n")
# -----------------------------------------------------------------


def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                logger.stdin.write(f"{'Finding Buy signal..' if ticker == 'KRW' else 'Finding Sell signal..'}  Balance: {float(b['balance'])}{ticker}  [{datetime.datetime.now().strftime('%H:%M:%S')}]\n".encode('utf-8'))
                logger.stdin.flush()
                return float(b['balance'])
            else:
                return 0

def buy_order(ticker, volume):
    try:
        while True:
            buy_result = upbit.buy_market_order(ticker, volume)
            if buy_result == None or 'error' in buy_result:
                print("매수 재 주문")
                time.sleep(1)
            else:
                return buy_result
    except:
        print("매수 주문 이상")


def sell_order(ticker, volume):
    try:
        while True:
            sell_result = upbit.sell_market_order(ticker, volume)
            if sell_result == None or 'error' in sell_result:
                print("매도 재 주문")
                time.sleep(1)
            else:
                return sell_result
    except:
        print("매도 주문 이상")


def log(_dict):
    diction = {"bid": "매수주문", "ask": "매도주문"}
    _created_at = _dict['created_at'][:10] + " " + _dict['created_at'][11:19]
    print(f"[{_created_at}] {_dict['market']} {diction[_dict['side']]} ({_dict['locked']})")


class Indicator:
    def __init__(self):
        self.df = pyupbit.get_ohlcv("KRW-BTC", interval="minute10", count=200)

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
    indicator = Indicator()
    cnt = True
    cnt = cnt and (True if indicator.now_stochastic()[0] < 80 and indicator.now_stochastic()[1] < 80 else False)
    cnt = cnt and (True if indicator.now_rsi() >= 50 else False)
    cnt = cnt and (True if indicator.now_macdOR() >= 0 else False)
    return cnt

def ask_check(): # 매도조건
    indicator = Indicator()
    cnt = 0
    cnt += 1 if indicator.now_stochastic()[0] >= 80 and indicator.now_stochastic()[1] >= 80 else 0
    cnt += 1 if indicator.now_rsi() <= 50 else 0
    cnt += 1 if indicator.now_macdOR() <= 0 else 0
    if cnt >= 2:
        return True
    else:
        return False

while True:
    try:
        while True:
            if get_balance("KRW") > 5000:
                if bid_check():
                    log(buy_order("KRW-BTC", get_balance("KRW")*0.9995))
                    time.sleep(0.5)
                    break
                time.sleep(0.5)
            else:
                break

            time.sleep(0.5)

        while True:
            if get_balance("BTC") > 0.00008:
                if ask_check():
                    log(buy_order("KRW-BTC", get_balance("BTC")*0.9995))
                    time.sleep(0.5)
                    break
                time.sleep(0.5)
            else:
                break

            time.sleep(0.5)

    except Exception as e:
        print(e)
        time.sleep(1)
        pass
