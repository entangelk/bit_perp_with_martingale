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

# 주문을 생성하는 함수 (TP/SL 포함)
def create_order_with_tp_sl(symbol, side, amount, price=None, tp_price=None, sl_price=None):
    try:
        params = {
            'symbol': symbol.replace('/', ''),  # Bybit 형식에 맞춰 변환
            'side': 'Buy' if side.lower() == 'buy' else 'Sell',  # 'Buy' 또는 'Sell'
            'qty': amount,
            'order_type': 'Limit' if price else 'Market',  # 지정가 또는 시장가 주문
            'reduce_only': False,  # 감축 주문 여부
            'close_on_trigger': False,  # 트리거 발생 시 포지션 종료
            'time_in_force': 'GoodTillCancel'  # 주문 지속시간
        }

        # 지정가 주문일 경우 가격 추가
        if price:
            params['price'] = price
        
        # Take Profit 설정
        if tp_price:
            params['take_profit'] = tp_price
        
        # Stop Loss 설정
        if sl_price:
            params['stop_loss'] = sl_price

        # 주문 생성
        order = exchange.private_post_order_create(params)
        print("주문 생성 성공 (TP/SL 포함):")
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
