from ib_insync import *
from ib_insync.contract import ContFuture
from ib_insync.ib import IB

ib = IB()
ib.connect()
ib.reqMarketDataType(3)


def place_order(direction, qty, df, tp, sl):
    bracket_order = ib.bracketOrder(
        direction,
        qty,
        limitPrice = round(df.close.iloc[-1]),
        takeProfitPrice = round(tp),
        stopLossPrice = round(sl),
    )

    for order in bracket_order:
        ib.placeOrder(contract, order)


def on_new_bar(data):
    global in_position
    
    df = util.df(data)
    sma = df.close.tail(50).mean()
    std_dev = df.close.tail(50).std() * 3
    print(f'SMA: {sma} | SD: {std_dev}')

    if df.close.iloc[-1] > sma + std_dev:
        # Trading more than 3 standard deviations above average - SELL
        try:
            place_order('SELL', 1, df, sma, sma + std_dev * 2)
        except Exception as e:
            print(e)

        in_position = True

        print('Sell order placed!')

    elif df.close.iloc[-1] < sma - std_dev:
        # Trading more than 3 standard deviations below average - BUY
        try:
            place_order('BUY', 1, df, sma,  sma - std_dev * 2)
        except Exception as e:
            print(e)

        in_position = True

        print('Buy order placed!')


# Create Contract
try:
    contract = ContFuture('HE', 'GLOBEX')
    ib.qualifyContracts(contract)
except Exception as e:
    print(e)
    
# Request Streaming bars
data = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='2 D',
    barSizeSetting='15 mins',
    whatToShow='MIDPOINT',
    useRTH=True,
    keepUpToDate=True,
)

in_position = False

while True:
    ib.sleep(300)
    on_new_bar(data)
    ib.sleep(2)
    if in_position == True:
        try:
            ib.disconnect()
        except Exception as e:
            print(e)
        break