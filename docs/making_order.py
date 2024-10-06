import ccxt
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Bybit API 키와 시크릿 가져오기
BYBIT_ACCESS_KEY = os.getenv("BYBIT_ACCESS_KEY")
BYBIT_SECRET_KEY = os.getenv("BYBIT_SECRET_KEY")

# Bybit 거래소 객체 생성 (선물 거래용)
exchange = ccxt.bybit({
    'apiKey': BYBIT_ACCESS_KEY,
    'secret': BYBIT_SECRET_KEY,
    'options': {
        'defaultType': 'swap',  # 무기한 선물(perpetual swap)
    },
    'enableRateLimit': True  # API 호출 속도 제한 관리 활성화
})

# 레버리지를 설정하는 함수
def set_leverage(symbol, leverage):
    try:
        # 레버리지 설정
        market = exchange.market(symbol)
        response = exchange.private_linear_post_position_set_leverage({
            'symbol': market['id'],  # 거래쌍 ID
            'buy_leverage': leverage,  # 매수 레버리지
            'sell_leverage': leverage  # 매도 레버리지
        })
        print(f"{symbol} 레버리지 설정 성공: {response}")
        return response

    except Exception as e:
        print(f"레버리지 설정 중 오류 발생: {e}")
        return None

def create_order_with_tp_sl(symbol, side, amount, leverage=100, price=None, tp_rate=0.20, sl_rate=0.20):
    try:
        # 주문 타입 결정 (지정가 또는 시장가)
        order_type = 'limit' if price else 'market'

        # 주문 기본 파라미터
        params = {
            'symbol': symbol,  # 예: 'BTC/USDT'
            'side': side.lower(),  # 'buy' 또는 'sell'
            'amount': amount,
            'type': order_type,  # 'limit' 또는 'market'
        }

        # 지정가 주문일 경우 가격 추가
        if price:
            params['price'] = price
        
        # 진입 가격을 기준으로 TP/SL을 수익률로 설정
        if price:
            entry_price = price  # 지정가일 경우 입력된 price 사용
        else:
            # 시장가 주문이라면, 현재 시장 가격을 기준으로 설정해야 함
            ticker = exchange.fetch_ticker(symbol)
            entry_price = ticker['last']  # 시장가의 현재 가격

        # TP/SL이 수익률로 제공될 경우 레버리지 고려하여 계산
        if tp_rate or sl_rate:
            params['params'] = {}

        # TP(테이크 프로핏) 수익률 설정 (레버리지 100배 반영)
        if tp_rate:
            # 수익률을 레버리지로 고려하여 목표 가격 계산 (0.2% 변화)
            if side.lower() == 'buy':
                tp_price = entry_price * (1 + (tp_rate / leverage))
            else:
                tp_price = entry_price * (1 - (tp_rate / leverage))
            params['params']['takeProfitPrice'] = tp_price
        
        # SL(스톱 로스) 수익률 설정 (레버리지 100배 반영)
        if sl_rate:
            # 손실률을 레버리지로 고려하여 목표 가격 계산 (0.2% 변화)
            if side.lower() == 'buy':
                sl_price = entry_price * (1 - (sl_rate / leverage))
            else:
                sl_price = entry_price * (1 + (sl_rate / leverage))
            params['params']['stopLossPrice'] = sl_price

        # CCXT에서 주문 생성
        order = exchange.create_order(
            symbol=params['symbol'], 
            type=params['type'], 
            side=params['side'], 
            amount=params['amount'], 
            price=params.get('price'), 
            params=params.get('params')
        )

        print("주문 생성 성공 (TP/SL 포함, 레버리지 100배 고려):")
        print(order)
        return order

    except Exception as e:
        print(f"주문 생성 중 오류 발생: {e}")
        return None


# 포지션을 청산하는 (시장가로 닫는) 함수
def close_position(symbol, side, amount):
    try:
        # 포지션을 닫는 반대 방향의 주문
        opposite_side = 'sell' if side.lower() == 'buy' else 'buy'
        close_order = exchange.create_order(symbol, 'market', opposite_side, amount, params={"reduce_only": True})
        print(f"포지션 청산 성공: {close_order}")
        return close_order
    except Exception as e:
        print(f"포지션 청산 중 오류 발생: {e}")
        return None


'''
# 예시: 레버리지 설정, 주문 생성 (TP/SL 포함)
symbol = "BTC/USDT"
leverage = 10  # 레버리지 10배 설정
amount = 0.01  # 0.01 BTC 주문
price = 30000  # 지정가 주문일 경우 가격
tp_price = 35000  # 테이크 프로핏 (수익 실현) 가격
sl_price = 29000  # 스탑로스 가격

# 레버리지 설정
set_leverage(symbol=symbol, leverage=leverage)

# 지정가 주문 생성 (TP/SL 포함)
create_order_with_tp_sl(symbol=symbol, side="Buy", amount=amount, price=price, tp_price=tp_price, sl_price=sl_price)
'''
