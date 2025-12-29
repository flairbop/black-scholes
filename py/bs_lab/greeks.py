import math
from .core import d1_d2, norm_pdf, norm_cdf

def bs_greeks(S, K, T, r, q, sigma, option_type="call"):
    """Computes Delta, Gamma, Vega, Theta, Rho."""
    if T <= 0:
        return {
            "delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0
        }
    
    # Validation/Clamp
    if sigma < 1e-9: sigma = 1e-9
    
    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    # nd1 = N'(d1)
    nd1 = norm_pdf(d1)
    
    exp_qT = math.exp(-q * T)
    exp_rT = math.exp(-r * T)
    sqrt_T = math.sqrt(T)
    
    # Gamma (same for call/put)
    gamma = (exp_qT * nd1) / (S * sigma * sqrt_T)
    
    # Vega (raw derivative dV/dSigma). Same for call/put.
    vega = S * exp_qT * nd1 * sqrt_T
    
    if option_type == "call":
        # Delta
        delta = exp_qT * norm_cdf(d1)
        
        # Rho (dV/dr)
        rho = K * T * exp_rT * norm_cdf(d2)
        
        # Theta (dV/dt, usually negative)
        # Term 1
        t1 = - (S * exp_qT * nd1 * sigma) / (2 * sqrt_T)
        # Term 2
        t2 = - r * K * exp_rT * norm_cdf(d2)
        # Term 3
        t3 = q * S * exp_qT * norm_cdf(d1)
        theta = t1 + t2 + t3
        
    else: # put
        # Delta
        delta = -exp_qT * norm_cdf(-d1)
        
        # Rho
        rho = -K * T * exp_rT * norm_cdf(-d2)
        
        # Theta
        t1 = - (S * exp_qT * nd1 * sigma) / (2 * sqrt_T)
        t2 = r * K * exp_rT * norm_cdf(-d2)
        t3 = - q * S * exp_qT * norm_cdf(-d1)
        theta = t1 + t2 + t3
    
    # Return RAW values. API/Formatting layer handles scaling (e.g. /100, /365).
    # Maintain numerical purity here.
    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega,
        "theta": theta,
        "rho": rho
    }
