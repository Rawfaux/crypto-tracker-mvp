# config.py

# --- API-Datenquelle ---
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,cardano,solana&vs_currencies=usd"

# Mapping von Symbol zu CoinGecko ID
COIN_MAPPING = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'ADA': 'cardano',
    'SOL': 'solana'
}