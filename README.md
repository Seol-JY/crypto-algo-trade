# Crypto_Algo_Trade
**Cryptocurrency algorithmic trading**  

![1](https://i.imgur.com/vZZGRhk.png)  


Upbit API를 활용  
Ta-lib 금융 보조지표 라이브러리를 활용한 기술적 분석을 통해  
매수, 매도시그널 탐색

## 매수전략
Stochastic값이 80미만이고  
RSI값이 50이상이며  
MACD Oscillator 값이 0 또는 양수일때 매수신호      

## 매도전략
Stochastic값이 80이상이거나  
RSI값이 50이하이거나  
MACD Oscillator 값이 0 또는 음수일때 매도신호

## 사용법
**access.txt** 에 Upbit거래소의 API key를 작성  
(첫줄에 Access key, 두번째줄에 Secret key)

