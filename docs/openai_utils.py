from openai import OpenAI

from docs.cal_chart import cal_chart
from dotenv import load_dotenv
import os
import json

# 포지션이 없을 때
def ai_choise(current_price, positions_json):

    load_dotenv()
    OPEN_API_KEY = os.getenv("OPEN_API_KEY")

    client = OpenAI(api_key=OPEN_API_KEY)

    # 분봉별 기술적 분석
    df_1m, df_5m, df_15m, df_1h, df_30d = cal_chart()

    df_1m = df_1m[-50:].to_json()
    df_5m = df_5m[-50:].to_json()
    df_15m = df_15m[-50:].to_json()
    df_1h = df_1h[-12:].to_json()
    df_30d = df_30d[-30:].to_json()


    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": """You are an expert in Bitcoin perpetual investing. Analyze the provided data including technical indicators, market data, recent news headlines, and the Fear and Greed Index. Based on the analysis, provide the following investment decisions:
                - Entry position (buy, stay, sell)
                - Take profit (TP) and Stop loss (SL) values
                - Leverage ratio (ensure it does not exceed 10x)
                - Entry price as a percentage of the capital

                Here is the data for your analysis:
                - Technical indicators and market data
                - Recent news headlines and their potential impact on Bitcoin price
                - The Fear and Greed Index and its implications
                - Overall market sentiment
                - Recent visual chart data (Base64 screenshot)
                """
            },
                        {
                "role": "user",
                "content": [
                    {
                        "type" : "text",
                        "text" : f"""
                    current_price : {current_price} USDT
    15m OHLCV with indicators (15 minute): {df_15m}
    Daily OHLCV with indicators (30 days): {df_30d}
    Hourly OHLCV with indicators (24 hours): {df_1h}

    Recent chart screenshot (Base64)
    """
            },
                       
                ]
            }
        ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "trading_decision",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "position": {"type": "string", "enum": ["buy", "stay", "sell"]},
                            "tp": {"type": "number"},
                            "sl": {"type": "number"},
                            "leverage": {"type": "integer"},
                            "entry_price_percentage": {"type": "number"},
                            "decision": {"type": "string"}
                        },
                        "required": ["position", "tp", "sl", "leverage", "entry_price_percentage", "decision"],
                        "additionalProperties": False
                    }
                }
            },
            max_tokens=4095,  # 최대 토큰 수 제한
            temperature=0.5,  # 응답의 다양성 제어
        )

    # 응답의 텍스트를 JSON 형식으로 변환
    response_content = response.choices[0].message.content
    response_json = json.loads(response_content)

    position = response_json['position']
    tp = response_json['tp']
    sl = response_json['sl']
    leverage = response_json['leverage']
    entry_price_percentage = response_json['entry_price_percentage']
    decision = response_json['decision']

    print(f"Position: {position}") 
    print(f"TP: {tp}") 
    print(f"SL: {sl}") 
    print(f"Leverage: {leverage} (Max 10x)")
    print(f"Entry Price (% of capital): {entry_price_percentage}")
    print(f"Decision: {decision}")

    return position, tp, sl, leverage, entry_price_percentage, decision


if __name__ == "__main__":
    ai_choise()
