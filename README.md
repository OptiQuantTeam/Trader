Reference

[python-binance](https://python-binance.readthedocs.io/en/latest/overview.html )
test
Order 

> limit
>
> - symbol
> - side
> - type
> - timeInForce
> - quantity
> - Price

> market
>
> - symbol
> - side
> - type
> - quantity

> OCO
>
> - symbol
> - side
> - stopLimitTimeInForce
> - stopPrice
> - price



JSON

{

​	Type: ORDER_TYPE,

​	Order:{

​			symbol:

​			side:

​			...

​		}

}

AI에서 JSON파일을 Interface로 전달한다.

Interface는 Type을 보고 현물/선물, 지정가/시장가를 결정한다.

그 후 Order의 내용을 보고 해당 설정의 거래를 요청한다.