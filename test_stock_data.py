from stock_tracker import StockTracker

print("Testing enhanced stock data...")

st = StockTracker()

# Test historical data generation
print("\n1. Testing historical data generation:")
data = st.get_historical_data(30)
print(f"Generated {len(data)} data points")

print("\nSample data:")
for d in data[:5]:
    print(f"{d['timestamp'][:10]}: {d['price']} DKK")

# Test API format
print("\n2. Testing API format:")
if data:
    print(f"First data point: {data[0]}")
    print(f"Data structure: {list(data[0].keys())}")
