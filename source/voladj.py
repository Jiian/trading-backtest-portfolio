def calculate_voladj_weights(prices_close, window = 50):
    return prices_close.shift(1).pct_change().rolling(window).mean() / prices_close.shift(1).pct_change().rolling(window).std()