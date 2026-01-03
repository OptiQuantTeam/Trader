from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import math

def futures_market_params(client, info, config, asset):
    quantity = _calculate_position_size(client, info['symbol'], info, asset, int(config['leverage']))
    sl = float(config['sl']) if info['positionSide'] == 'LONG' else -float(config['sl'])
    tp = float(config['tp']) if info['positionSide'] == 'LONG' else -float(config['tp'])
    
    slprice = info['price']*(1-sl/(int(config['leverage'])*100))
    tpprice = info['price']*(1+tp/(int(config['leverage'])*100))

    return {
            'symbol': info['symbol'],
            'side' : info['side'],
            'positionSide' : info['positionSide'],
            'type' : config['type'],
            'sl' : slprice,
            'tp' : tpprice,
            'quantity' : quantity,
            'leverage' : int(config['leverage'])
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
        
        # 수입 내역이 3개 미만인 경우 처리
        if len(income) < 3:
            return income  # 가능한 만큼의 수입 내역 반환
            
        return income[-3:]  # 최근 3개의 수입 내역
    except Exception as e:
        return []

def adjust_leverage(income, current_leverage):
    """
    수익 내역에 따라 레버리지를 조정합니다.
    - 2연속 수익 시 레버리지 1단계 상승
    - 1회 실패 시 레버리지 1단계 하락
    
    Args:
        income (list): 최근 수익 내역 (최신순)
        current_leverage (int): 현재 레버리지
    
    Returns:
        int: 조정된 레버리지
    """
    if len(income) < 2:  # 최소 2개의 거래 내역이 필요
        return current_leverage
        
    max_leverage = 8
    min_leverage = 1
    
    # 최근 2개 거래의 수익 확인
    last_two_trades = income[:2]
    
    # 2연속 수익인 경우
    if last_two_trades[0] > 0 and last_two_trades[1] > 0:
        return min(current_leverage * 2, max_leverage)
    
    # 2연속 실패인 경우
    if last_two_trades[0] < 0 and last_two_trades[1] < 0:
        return max(current_leverage // 2, min_leverage)
    
    # 그 외의 경우 (1승 1패 등) 현재 레버리지 유지
    return current_leverage

def get_leverage_settings(leverage: int) -> dict:
    """
    레버리지에 따른 로스컷, 익절, 포지션 비중 설정을 반환합니다.
    
    Args:
        leverage (int): 레버리지 배수 (1, 2, 4, 8)
    
    Returns:
        dict: 로스컷 비율, 익절 비율, 포지션 비중 설정
    """
    settings = {
        1: {'stop_loss': 0.02, 'take_profit': 0.04, 'position_ratio': 0.70},  # 2% 로스컷, 4% 익절, 70% 비중
        2: {'stop_loss': 0.015, 'take_profit': 0.03, 'position_ratio': 0.60},  # 3% 로스컷, 6% 익절, 60% 비중
        4: {'stop_loss': 0.01, 'take_profit': 0.02, 'position_ratio': 0.50},  # 4% 로스컷, 8% 익절, 50% 비중
        8: {'stop_loss': 0.0075, 'take_profit': 0.015, 'position_ratio': 0.40}   # 6% 로스컷, 12% 익절, 40% 비중
    }
    
    return settings.get(leverage, settings[2])  # 기본값은 2배 설정

def calculate_take_profit_price(entry_price: float, position_side: str, leverage: int) -> float:
    """
    진입가격과 포지션 방향에 따라 익절 가격을 계산합니다.
    
    Args:
        entry_price (float): 진입 가격
        position_side (str): 포지션 방향 ('LONG' 또는 'SHORT')
        leverage (int): 레버리지 배수
    
    Returns:
        float: 계산된 익절 가격
    """
    settings = get_leverage_settings(leverage)
    take_profit_ratio = settings['take_profit']
    
    if position_side == 'BUY':
        return round(entry_price * (1 + take_profit_ratio), 2)
    else:  # SHORT
        return round(entry_price * (1 - take_profit_ratio), 2)

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
    
    filters = {f['filterType']: f for f in symbol_info['filters']}

    lot_filter = filters['LOT_SIZE']
    min_qty = float(lot_filter['minQty'])
    step_size = float(lot_filter['stepSize'])
    min_notional = float(filters['MIN_NOTIONAL']['notional'])

    # 현재 가격
    current_price = float(info['price'])
    if current_price <= 0:
        raise ValueError('Invalid Price')

    # 레버리지 설정에 따른 포지션 비중 가져오기
    settings = get_leverage_settings(leverage)
    position_ratio = settings['position_ratio']

    target_notional = available_balance * position_ratio
    if target_notional < min_notional:
        required_balance = min_notional / position_ratio
        if available_balance < min_notional:
            raise ValueError(
                f"잔고 부족: 최소 주문 금액 {min_notional} USDT가 필요하지만 현재 {available_balance:.2f} USDT만 있습니다."
            )
        target_notional = min_notional

    raw_qty = target_notional / current_price
    qty_base = max(raw_qty, min_qty, min_notional/current_price)

    precision = int(round(-math.log10(step_size), 0))
    adjusted_quantity = math.ceil(qty_base/step_size) * step_size
    adjusted_quantity = round(adjusted_quantity, precision)

    actual_notional = adjusted_quantity * current_price
    if actual_notional < min_notional:
        raise ValueError(
            f"주문 금액 부족: {actual_notional:.2f} < {min_notional}"
        )
   
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
    
    if position_side == 'BUY':
        return round(entry_price * (1 - stop_loss_ratio), 2)
    else:  # SHORT
        return round(entry_price * (1 + stop_loss_ratio), 2)

def process_trade_logic(client, symbol: str, order_side: str, order_quantity: float, order_type: str, order_price: float = None, time_in_force: str = None, leverage: int = 2):
    """
    Processes a futures trade based on the current position and new order details.
    - If no position exists for the symbol, places the new order.
    - If a position exists and the new order is in the same direction, does nothing.
    - If a position exists and the new order is in the opposite direction, closes the entire existing position with a market order.
    
    Args:
        client: Binance API client instance.
        symbol (str): The trading symbol (e.g., 'BTCUSDT').
        order_side (str): The side of the order ('BUY' or 'SELL').
        order_quantity (float): The quantity for the new order.
        order_type (str): The type of the order (e.g., 'MARKET', 'LIMIT').
        order_price (float, optional): The price for LIMIT orders. Defaults to None.
        time_in_force (str, optional): Time in force for LIMIT orders (e.g., 'GTC'). Defaults to None.
        leverage (int, optional): 레버리지 배수. Defaults to 2.

    Returns:
        dict or None: The order response from Binance if an order is placed, otherwise None.
    """
    
    # HOLD 신호가 오면 아무것도 하지 않음
    if order_side == 'HOLD':
        return None
    
    # Use the existing get_position function to get the signed position amount
    # get_position returns the float amount or None if no position
    raw_pos_amt = get_position(client, symbol)
    current_pos_amt = float(raw_pos_amt) if raw_pos_amt is not None else 0.0

    current_pos_direction = None
    if current_pos_amt > 0:
        current_pos_direction = Client.SIDE_BUY  # Indicates a LONG position
    elif current_pos_amt < 0:
        current_pos_direction = Client.SIDE_SELL  # Indicates a SHORT position
    
    # Case 1: No position currently held for the symbol
    if current_pos_direction is None:
        try:
            # 기존 예약 주문 취소
            client.futures_cancel_all_algo_open_orders(symbol=symbol)

            params = {
                'symbol': symbol,
                'side': order_side,
                'type': order_type,
                'quantity': order_quantity,
            }
            if order_type == Client.ORDER_TYPE_LIMIT:
                if order_price is None:
                    return None
                params['price'] = order_price
                if time_in_force: # Common for LIMIT orders
                    params['timeInForce'] = time_in_force

            # 새로운 포지션이 열릴 때만 레버리지 변경
            client.futures_change_leverage(leverage=leverage, symbol=symbol)
            
            new_order = client.futures_create_order(**params)
            
            return new_order
        except BinanceAPIException as e:
            print(f'BinanceAPIException: {e}')
            return None
        except Exception as e:
            print(f'Exception: {e}')
            return None
    '''
    # Case 2: A position currently exists for the symbol
    else:
        # Subcase 2.1: New order is in the same direction as the current position
        if order_side == current_pos_direction:
            return None
        
        # Subcase 2.2: New order is in the opposite direction – close the existing position
        else:
            close_order_side = Client.SIDE_SELL if current_pos_direction == Client.SIDE_BUY else Client.SIDE_BUY
            # Quantity for closing is the absolute amount of the current position
            close_quantity = abs(current_pos_amt) 

            try:
                closing_order = client.futures_create_order(
                    symbol=symbol,
                    side=close_order_side,
                    type=Client.ORDER_TYPE_MARKET,  # Typically close positions with a market order for certainty
                    quantity=close_quantity,
                    reduceOnly=True  # Ensures this order only reduces or closes the position
                )

                # 포지션 정리 후에 해당 심볼의 모든 예약 주문 취소
                client.futures_cancel_all_open_orders(symbol=symbol)

                return closing_order
            except BinanceAPIException as e:
                return None
            except Exception as e:
                return None
    '''
def process_test_trade_logic(client, symbol: str, order_side: str, order_quantity: float, order_type: str, order_price: float = None, time_in_force: str = None, leverage: int = 2):
    """
    Processes a futures trade based on the current position and new order details.
    - If no position exists for the symbol, places the new order.
    - If a position exists and the new order is in the same direction, does nothing.
    - If a position exists and the new order is in the opposite direction, closes the entire existing position with a market order.
    
    Args:
        client: Binance API client instance.
        symbol (str): The trading symbol (e.g., 'BTCUSDT').
        order_side (str): The side of the order ('BUY' or 'SELL').
        order_quantity (float): The quantity for the new order.
        order_type (str): The type of the order (e.g., 'MARKET', 'LIMIT').
        order_price (float, optional): The price for LIMIT orders. Defaults to None.
        time_in_force (str, optional): Time in force for LIMIT orders (e.g., 'GTC'). Defaults to None.

    Returns:
        dict or None: The order response from Binance if an order is placed, otherwise None.
    """
    
    # Use the existing get_position function to get the signed position amount
    # get_position returns the float amount or None if no position
    raw_pos_amt = get_position(client, symbol)
    current_pos_amt = float(raw_pos_amt) if raw_pos_amt is not None else 0.0

    current_pos_direction = None
    if current_pos_amt > 0:
        current_pos_direction = Client.SIDE_BUY  # Indicates a LONG position
    elif current_pos_amt < 0:
        current_pos_direction = Client.SIDE_SELL  # Indicates a SHORT position

    # Case 1: No position currently held for the symbol
    if current_pos_direction is None:
        try:
            params = {
                'symbol': symbol,
                'side': order_side,
                'type': order_type,
                'quantity': order_quantity,
            }
            if order_type == Client.ORDER_TYPE_LIMIT:
                if order_price is None:
                    return None
                params['price'] = order_price
                if time_in_force: # Common for LIMIT orders
                    params['timeInForce'] = time_in_force
            
            # 여기에 수량 및 가격 정밀도 조정 로직을 추가할 수 있습니다.
            # 예: adjusted_params = adjust_order_params(client, symbol, quantity=order_quantity, price=order_price if order_type == Client.ORDER_TYPE_LIMIT else None)
            # params['quantity'] = adjusted_params['quantity']
            # if 'price' in adjusted_params:
            #     params['price'] = adjusted_params['price']

            # 새로운 포지션이 열릴 때만 레버리지 변경
            client.futures_change_leverage(leverage=leverage, symbol=symbol)
            new_order = client.futures_create_test_order(**params)
            return new_order
        except BinanceAPIException as e:
            return None
        except Exception as e:
            return None

    # Case 2: A position currently exists for the symbol
    else:
        # Subcase 2.1: New order is in the same direction as the current position
        if order_side == current_pos_direction:
            return None
        
        # Subcase 2.2: New order is in the opposite direction – close the existing position
        else:
            
            close_order_side = Client.SIDE_SELL if current_pos_direction == Client.SIDE_BUY else Client.SIDE_BUY
            # Quantity for closing is the absolute amount of the current position
            close_quantity = abs(current_pos_amt) 

            try:
                closing_order = client.futures_create_test_order(
                    symbol=symbol,
                    side=close_order_side,
                    type=Client.ORDER_TYPE_MARKET,  # Typically close positions with a market order for certainty
                    quantity=close_quantity,
                    reduceOnly=True  # Ensures this order only reduces or closes the position
                )
                return closing_order
            except BinanceAPIException as e:
                return None
            except Exception as e:
                return None
            
def get_symbol_info(client, symbol: str) -> dict:
    """
    거래쌍의 상세 정보를 가져옵니다.
    
    Args:
        client: 바이낸스 클라이언트
        symbol (str): 거래쌍 심볼
    
    Returns:
        dict: 거래쌍 정보 (찾지 못한 경우 None)
    """
    try:
        exchange_info = client.futures_exchange_info()
        for symbol_info_item in exchange_info['symbols']:
            if symbol_info_item['symbol'] == symbol:
                return symbol_info_item
    except BinanceAPIException as e:
        return None
    except Exception as e:
        return None
    