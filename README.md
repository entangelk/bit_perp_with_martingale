# bitcoin perpatual trading with martingale'stg




## 데이터 구조
1. 포지션
- 수수료(str) : position['info']['curRealisedPnl']
    * positions_data = json.loads(positions_json)
    * positions_data[0]['info']['curRealisedPnl']
- 현재수익(str) : position['info']['unrealizedPnl']
2. 이전 거래 기록
- ledger : json데이터(리스트 형식)
```
ledger[-1]
{'id': '629729', 'timestamp': 1728241520885, 'datetime': '2024-10-06T19:05:20.885Z', 'direction': 'in', 'account': None, 'referenceId': None, 'referenceAccount': None, 'type': 'trade', 'currency': 'USDT', 'amount': 0.10136311, 'before': 250.67424045, 'after': 250.77560356, 'status': 'ok', 'fee': {'currency': 'USDT', 'cost': 0.02763689}, 'info': {'id': '629729', 'symbol': 'BTCUSDT', 'category': 'linear', 'side': 'Sell', 'transactionTime': '1728241520885', 'type': 'TRADE', 'qty': '0.001', 'size': '0.000', 'currency': 'USDT', 'tradePrice': '62811.10', 'funding': '', 'fee': '0.02763689', 'cashFlow': '0.12900000', 'change': '0.10136311', 'cashBalance': '250.77560356', 'feeRate': '0.00044000', 'bonusChange': '', 'tradeId': '4a6d14c9-a351-597b-a34a-bab85fece77f', 'orderId': '142eb168-0b38-4b78-99c1-ea815343afac', ...}}
```
- 마지막 거래 이익 계산 : direction이 out일때 amount를 모두 더해서 in일때 amount에서 차감

## 마틴게일 전략 적용
1. 레버리지 : 100배
2. 시작 목표 수익 : 2달라
3. 오픈 포지션량 : 10달라



## 해야할 일
TP/SL이 지금 제대로 계산이 안되고 있음 이거를 다시 계산해야됨
방안 1. 일단 시장가로 주문 후, 바로 TP/SL을 계산하여 넣기
방안 2. 다시 계산해서 시장가 주문 시 같이 넣기

ai에게 물어보는거에 1분봉과 5분봉을 중점으로 보라고 해야됨 -> 레버리지 100배이니까 장기적 관점보다는 단기적 관점으로, 단기적 추세가 꺽이는것에 주의

결과 백테스킹 구현