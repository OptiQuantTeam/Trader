
def futures_market_params(event, config, balance):
    quantity = '{:.8f}'.format((float(balance['free'])*float(config['ratio']))/(float(event['price'])*100))
    
    sl = float(config['sl']) if event['positionSide'] == 'LONG' else -float(config['sl'])
    tp = float(config['tp']) if event['positionSide'] == 'LONG' else -float(config['tp'])
    
    slprice = event['price']*(1-sl/(float(config['leverage'])*100))
    tpprice = event['price']*(1+tp/(float(config['leverage'])*100))

    return {
            'symbol': event['symbol'],
            'side' : event['side'],
            'positionSide' : event['positionSide'],
            'type' : config['type'],
            'sl' : slprice,
            'tp' : tpprice,
            'quantity' : quantity
            }

def futures_limit_params(event, config, balance):
    quantity = '{:.8f}'.format((float(balance['free'])*float(config['ratio']))/(float(event['price'])*100))
    
    sl = float(config['sl']) if event['positionSide'] == 'LONG' else -float(config['sl'])
    tp = float(config['tp']) if event['positionSide'] == 'LONG' else -float(config['tp'])
    
    slprice = event['price']*(1-sl/(float(config['leverage'])*100))
    tpprice = event['price']*(1+tp/(float(config['leverage'])*100))
    
    return {
            'symbol': event['symbol'],
            'side' : event['side'],
            'positionSide' : event['positionSide'],
            'type' : config['type'],
            'quantity' : quantity,
            'price' : event['price'],
            'sl' : slprice,
            'tp' : tpprice
            }

def spot_market_params(event, config, balance):
    quantity = '{:.8f}'.format((float(balance['free'])*float(config['ratio']))/(float(event['price'])*100))
    
    slprice = event['price']*(1-float(config['sl'])/(float(config['leverage'])*100))
    tpprice = event['price']*(1+float(config['tp'])/(float(config['leverage'])*100))

    return {
            'symbol': event['symbol'],
            'side' : event['side'],
            'type' : config['type'],
            'quantity' : quantity,
            'sl' : slprice,
            'tp' : tpprice
            }

def spot_limit_params(event, config, balance):
    quantity = '{:.8f}'.format((float(balance['free'])*float(config['ratio']))/(float(event['price'])*100))
    
    slprice = event['price']*(1-float(config['sl'])/(float(config['leverage'])*100))
    tpprice = event['price']*(1+float(config['tp'])/(float(config['leverage'])*100))

    return {
            'symbol': event['symbol'],
            'side' : event['side'],
            'type' : config['type'],
            'quantity' : quantity,
            'price' : event['price'],
            'sl' : slprice,
            'tp' : tpprice
            }