
def futures_market_params(info, config, asset):
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