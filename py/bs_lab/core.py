import math

def norm_pdf(x):
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def norm_cdf(x):
    """Standard normal cumulative distribution function (Abramowitz & Stegun)."""
    # Use erf for standard implementation in Python math
    return 0.5 * (1 + math.erf(x / math.sqrt(2.0)))

def d1_d2(S, K, T, r, q, sigma):
    """Computes d1 and d2 terms for Black-Scholes."""
    if T <= 0 or sigma <= 0:
        return 0.0, 0.0
        
    sqrt_T = math.sqrt(T)
    # math.log(S/K) handles positive S, K. Checked in caller.
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return d1, d2

def bs_price(S, K, T, r, q, sigma, option_type="call"):
    """Computes Black-Scholes price for call or put."""
    # Boundary / Limits
    if S <= 0 or K <= 0: return 0.0
    if T <= 0:
        return max(0.0, S - K) if option_type == "call" else max(0.0, K - S)
    if sigma < 1e-9:
        # Intrinsic approx (discounted)
        fwd = S * math.exp((r-q)*T)
        val = max(0.0, fwd - K) if option_type == "call" else max(0.0, K - fwd)
        return val * math.exp(-r*T)

    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    
    if option_type == "call":
        price = S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)
        
    return max(0.0, price)
