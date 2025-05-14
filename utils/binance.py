from datetime import datetime, timedelta

def futures_market_params(client, info, config, asset, leverage):
    quantity = _calculate_position_size(client, info['symbol'], info, asset, leverage)
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
    max_leverage = 4
    min_leverage = 1

    if income[0] > 0 and income[1] > 0 and income[2] > 0:
        return min(current_leverage + 1, max_leverage)
    elif income[0] < 0 and income[1] < 0 and income[2] < 0:
        return max(current_leverage - 1, min_leverage)
    else:
        return current_leverage

def get_leverage_settings(leverage: int) -> dict:
    """
    레버리지에 따른 로스컷과 포지션 비중 설정을 반환합니다.
    
    Args:
        leverage (int): 레버리지 배수 (1-4)
    
    Returns:
        dict: 로스컷 비율과 포지션 비중 설정
    """
    settings = {
        4: {'stop_loss': 0.10, 'position_ratio': 0.30},  # 10% 로스컷, 30% 비중
        3: {'stop_loss': 0.075, 'position_ratio': 0.40}, # 7.5% 로스컷, 40% 비중
        2: {'stop_loss': 0.05, 'position_ratio': 0.50},  # 5% 로스컷, 50% 비중
        1: {'stop_loss': 0.025, 'position_ratio': 0.60}  # 2.5% 로스컷, 60% 비중
    }
    
    return settings.get(leverage, settings[2])  # 기본값은 2배 설정

def _calculate_position_size(client, symbol: str, info: dict, available_balance: float, leverage: int) -> float:
    """
    레버리지와 계좌 잔고에 따른 적정 포지션 수량을 계산합니다.
    
    Args:
        client: 바이낸스 클라이언트
        symbol (str): 거래 심볼
        info (dict): 심볼 정보
        available_balance (float): 사용 가능한 잔고 (USDT)
        leverage (int): 레버리지 배수
    
    Returns:
        float: 적정 포지션 수량 (예: BTC의 경우 0.001 등)
    """
    # 심볼 정보 조회
    exchange_info = client.futures_exchange_info()
    symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
    
    if not symbol_info:
        raise ValueError(f"Symbol {symbol} not found")
    
    # 현재 가격
    current_price = float(info['price'])
    
    # 최소 수량 단위 (step_size) 설정
    step_size = float(next(f['stepSize'] for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE'))
    
    # 레버리지 설정에 따른 포지션 비중 가져오기
    settings = get_leverage_settings(leverage)
    position_ratio = settings['position_ratio']
    
    # USDT 기준 포지션 크기 계산
    position_size_usdt = round(available_balance * position_ratio, 2)
    
    # 수량으로 변환
    quantity = position_size_usdt / current_price
    
    # step_size에 맞게 수량 조정
    decimal_places = len(str(step_size).split('.')[1]) if '.' in str(step_size) else 0
    adjusted_quantity = round(quantity / step_size) * step_size
    adjusted_quantity = round(adjusted_quantity, decimal_places)
    
    return adjusted_quantity

def calculate_stop_loss_price(entry_price: float, position_side: str, leverage: int) -> float:
    """
    진입가격과 포지션 방향에 따라 스탑로스 가격을 계산합니다.
    
    Args:
        entry_price (float): 진입 가격
        position_side (str): 포지션 방향 ('LONG' 또는 'SHORT')
        leverage (int): 레버리지 배수
    
    Returns:
        float: 계산된 스탑로스 가격
    """
    settings = get_leverage_settings(leverage)
    stop_loss_ratio = settings['stop_loss']
    
    if position_side == 'LONG':
        return round(entry_price * (1 - stop_loss_ratio), 2)
    else:  # SHORT
        return round(entry_price * (1 + stop_loss_ratio), 2)
    