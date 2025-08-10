import yfinance as yf

print("Testing Brøndby IF stock symbols...")

symbols = ['BIF.CO', 'BRNDBY.CO', 'BRNDBY', 'BRNDBY-USD', 'BRNDBY.DK', 'BRNDBY.OL']

for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice', 'Not found')
        name = info.get('longName', 'Unknown')
        print(f"{symbol}: {price} - {name}")
    except Exception as e:
        print(f"{symbol}: Error - {e}")

print("\nTesting some known Danish stocks...")
danish_symbols = ['NOVO-B.CO', 'VWS.CO', 'CARL-B.CO']

for symbol in danish_symbols:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice', 'Not found')
        name = info.get('longName', 'Unknown')
        print(f"{symbol}: {price} - {name}")
    except Exception as e:
        print(f"{symbol}: Error - {e}")
