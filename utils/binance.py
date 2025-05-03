from datetime import datetime, timedelta

def futures_market_params(info, config, asset):
    #quantity = '{:.8f}'.format((float(asset)*float(config['ratio']))/(float(info['price'])*100))
    quantity = '{:.3f}'.format((float(asset))/(float(info['price'])))
    print(quantity)
    sl = float(config['sl']) if info['positionSide'] == 'LONG' else -float(config['sl'])
    tp = float(config['tp']) if info['positionSide'] == 'LONG' else -float(config['tp'])
    
    slprice = info['price']*(1-sl/(float(config['leverage'])*100))
    tpprice = info['price']*(1+tp/(float(config['leverage'])*100))

    return {
            'symbol': info['symbol'],
            'side' : info['side'],
            'positionSide' : info['positionSide'],
            'type' : config['type'],
            'sl' : slprice,
            'tp' : tpprice,
            'quantity' : quantity
            }


def futures_limit_params(info, config, asset):
    quantity = '{:.8f}'.format((float(asset)*float(config['ratio']))/(float(info['price'])*100))
    
    sl = float(config['sl']) if info['positionSide'] == 'LONG' else -float(config['sl'])
    tp = float(config['tp']) if info['positionSide'] == 'LONG' else -float(config['tp'])
    
    slprice = info['price']*(1-sl/(float(config['leverage'])*100))
    tpprice = info['price']*(1+tp/(float(config['leverage'])*100))
    
    return {
            'symbol': info['symbol'],
            'side' : info['side'],
            'positionSide' : info['positionSide'],
            'type' : config['type'],
            'quantity' : quantity,
            'price' : info['price'],
            'sl' : slprice,
            'tp' : tpprice
            }

def spot_market_params(info, config, asset):
    quantity = '{:.8f}'.format((float(asset)*float(config['ratio']))/(float(info['price'])*100))
    
    slprice = info['price']*(1-float(config['sl'])/(float(config['leverage'])*100))
    tpprice = info['price']*(1+float(config['tp'])/(float(config['leverage'])*100))

    return {
            'symbol': info['symbol'],
            'side' : info['side'],
            'type' : config['type'],
            'quantity' : quantity,
            'sl' : slprice,
            'tp' : tpprice
            }

def spot_limit_params(info, config, asset):
    quantity = '{:.8f}'.format((float(asset)*float(config['ratio']))/(float(info['price'])*100))
    
    slprice = info['price']*(1-float(config['sl'])/(float(config['leverage'])*100))
    tpprice = info['price']*(1+float(config['tp'])/(float(config['leverage'])*100))

    return {
            'symbol': info['symbol'],
            'side' : info['side'],
            'type' : config['type'],
            'quantity' : quantity,
            'price' : info['price'],
            'sl' : slprice,
            'tp' : tpprice
            }

def get_position(client, symbol):
    try:
        positions = client.futures_position_information(symbol=symbol)
        # 실제 보유중인 포지션만 필터링 (수량이 0이 아닌 것)
        active_positions = [
            {
                'symbol': pos['symbol'],
                'positionAmt': float(pos['positionAmt']),
                'entryPrice': float(pos['entryPrice']),
                'markPrice': float(pos['markPrice']),
                'unrealizedProfit': float(pos['unRealizedProfit']),
                'liquidationPrice': float(pos['liquidationPrice']),
                'leverage': int(pos['leverage']),
                'positionSide': pos['positionSide']
            }
            for pos in positions
            if float(pos['positionAmt']) != 0
        ]

        if not active_positions:
            print(f"{symbol}에 대한 활성 포지션이 없습니다.")
            return None

        position = active_positions[0]
        position_amt = position['positionAmt']
        
        return position_amt
    
    except Exception as e:
        print(e)

def get_income(client, symbol):
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=29)).timestamp() * 1000)
    try:
        response = client.futures_income_history(symbol=symbol, incomeType='REALIZED_PNL', endTime=end_time, startTime=start_time)
        income = [float(item['income']) for item in response]
        return income[-3:]  # 최근 3개의 수입 내역
    except Exception as e:
        print(e)

def adjust_leverage(income, current_leverage):
    if len(income) < 2:
        return current_leverage
    max_leverage = 10
    min_leverage = 1

    if income[0] > 0 and income[1] > 0 and income[2] > 0:
        return min(current_leverage + 1, max_leverage)
    elif income[0] < 0 and income[1] < 0 and income[2] < 0:
        return max(current_leverage - 1, min_leverage)
    else:
        return current_leverage

def adjust_stop_loss(leverage: int, base_sl: float) -> float:
    """
    레버리지에 따라 스탑로스를 조정합니다.
    
    Args:
        leverage (int): 현재 레버리지
        base_sl (float): 기본 스탑로스 비율 (예: 0.01 = 1%)
    
    Returns:
        float: 조정된 스탑로스 비율
    """
    # 레버리지가 높을수록 스탑로스를 더 낮게 설정
    adjustment_factor = 1 + (leverage - 1) * 0.1
    adjusted_sl = base_sl / adjustment_factor
    
    # 최소 스탑로스 제한 (0.1%)
    min_sl = 0.001
    return round(max(adjusted_sl, min_sl), 2)

def calculate_stop_loss_price(entry_price: float, position_side: str, leverage: int, base_sl: float) -> float:
    """
    진입가격과 포지션 방향에 따라 스탑로스 가격을 계산합니다.
    
    Args:
        entry_price (float): 진입 가격
        position_side (str): 포지션 방향 ('LONG' 또는 'SHORT')
        leverage (int): 현재 레버리지
        base_sl (float): 기본 스탑로스 비율
    
    Returns:
        float: 계산된 스탑로스 가격
    """
    adjusted_sl = adjust_stop_loss(leverage, base_sl)
    
    if position_side == 'LONG':
        return round(entry_price * (1 - adjusted_sl), 2)
    else:  # SHORT
        return round(entry_price * (1 + adjusted_sl), 2)
    