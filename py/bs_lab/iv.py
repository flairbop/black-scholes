from .core import bs_price
import math

ERROR_ARBITRAGE = "Arbitrage violation: Price out of bounds"
ERROR_CONVERGENCE = "Solver failed to converge"

def implied_volatility(market_price, S, K, T, r, q, option_type="call"):
    """
    Computes implied volatility using bisection method.
    Metrics: sigma in [1e-6, 5.0]
    """
    # 0. Pre-checks
    if T <= 0:
        return {"iv": 0.0, "status": "expired"}
    
    # 1. Arbitrage Bounds
    exp_rT = math.exp(-r * T)
    exp_qT = math.exp(-q * T)
    
    if option_type == "call":
        lower_bound = max(0.0, S * exp_qT - K * exp_rT)
        upper_bound = S * exp_qT
    else:
        lower_bound = max(0.0, K * exp_rT - S * exp_qT)
        upper_bound = K * exp_rT
    
    # Allow small epsilon tolerance for float errors
    epsilon = 1e-7
    if market_price < lower_bound - epsilon or market_price > upper_bound + epsilon:
        return {"iv": None, "status": ERROR_ARBITRAGE, "bounds": (lower_bound, upper_bound)}
        
    # If price is at lower bound (intrinsic), IV is 0 (or undefined/low).
    if abs(market_price - lower_bound) < epsilon:
        return {"iv": 0.0, "status": "intrinsic"}
        
    # 2. Bisection Solver
    # Sigma bounds
    low = 1e-6
    high = 5.0
    
    # Check bounds values
    p_low = bs_price(S, K, T, r, q, low, option_type)
    p_high = bs_price(S, K, T, r, q, high, option_type)
    
    # If market price is outside the price range accessible by sigma in [1e-6, 5.0]
    if market_price < p_low:
        return {"iv": low, "status": "clipped_low"}
    if market_price > p_high:
        return {"iv": high, "status": "clipped_high"}
        
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
            # Price is increasing with vol (Vega > 0 almost always)
            # If p_mid > market, we need lower vol
            high = mid
        else:
            low = mid
            
        inv_iter += 1
        
    return {"iv": mid, "status": "converged_tol", "iterations": inv_iter}
