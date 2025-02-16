
def futures_market_params(event, config, balance):
    quantity = (float(balance['free'])*float(config['ratio']))/(event['price']*100)

    return {
            'symbol': event['symbol'],
            'side' : event['side'],
            'type' : config['type'],
            'quantity' : str(quantity)
            }