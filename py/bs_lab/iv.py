from .core import bs_price
from .greeks import bs_greeks
import math

ERROR_ARBITRAGE = "Arbitrage violation: Price out of bounds"

def implied_volatility(market_price, S, K, T, r, q, option_type="call"):
    """
    Computes implied volatility using bisection method.
    Metrics: sigma in [1e-6, 5.0]
    """
    # 0. Pre-checks
    if T <= 0:
        return {"iv": 0.0, "status": "expired"}
    if market_price <= 0:
        return {"iv": None, "status": "invalid_price"}
    
    # 1. Arbitrage Bounds
    exp_rT = math.exp(-r * T)
    exp_qT = math.exp(-q * T)
    
    if option_type == "call":
        # Lower bound: Intrinsic value (discounted S - discounted K)
        # Upper bound: Stock price (discounted)
        lower_bound = max(0.0, S * exp_qT - K * exp_rT)
        upper_bound = S * exp_qT
    else:
        # Lower bound: Intrinsic value
        # Upper bound: Strike price (discounted)
        lower_bound = max(0.0, K * exp_rT - S * exp_qT)
        upper_bound = K * exp_rT
    
    # Allow small epsilon tolerance for float errors
    epsilon = 1e-7
    if market_price < lower_bound - epsilon or market_price > upper_bound + epsilon:
        return {"iv": None, "status": ERROR_ARBITRAGE, "bounds": (lower_bound, upper_bound)}
        
    # If price is at lower bound (intrinsic), IV is 0 defined limit.
    if abs(market_price - lower_bound) < epsilon:
        return {"iv": 0.0, "status": "intrinsic"}
        
    # 2. Bisection Solver
    low = 1e-6
    high = 5.0
    
    # Check if price achievable within bounds
    p_low = bs_price(S, K, T, r, q, low, option_type)
    p_high = bs_price(S, K, T, r, q, high, option_type)
    
    if market_price < p_low:
        return {"iv": low, "status": "clipped_low"} # Vol is < 1e-6
    if market_price > p_high:
        return {"iv": high, "status": "clipped_high"} # Vol is > 5.0
        
    # Bisect
    inv_iter = 0
    max_iter = 100
    tol = 1e-7
    
    while inv_iter < max_iter:
        mid = (low + high) / 2.0
        p_mid = bs_price(S, K, T, r, q, mid, option_type)
        
        diff = p_mid - market_price
        
        if abs(diff) < tol:
            return {"iv": mid, "status": "ok", "iterations": inv_iter}
        
        if diff > 0:
            # Price (almost always) monotonic in Vol. If p_mid too high, reduce vol.
            high = mid
        else:
            low = mid
            
        inv_iter += 1
        
    return {"iv": mid, "status": "converged_tol", "iterations": inv_iter}
