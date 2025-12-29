import math

def norm_pdf(x):
    """Standard normal probability density function."""
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)

def norm_cdf(x):
    """Standard normal cumulative distribution function."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2.0)))

def d1_d2(S, K, T, r, q, sigma):
    """Computes d1 and d2 terms for Black-Scholes."""
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return d1, d2

def bs_price(S, K, T, r, q, sigma, option_type="call"):
    """Computes Black-Scholes price for call or put."""
    if T <= 0:
        # Intrinsic value at expiry
        if option_type == "call":
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)
    
    # Avoid division by zero if sigma is very small
    if sigma < 1e-9:
        # Intrinsic approx
        val = S * math.exp((r-q)*T) - K
        if option_type == "call":
            return max(0.0, (S * math.exp(-q*T) - K * math.exp(-r*T))) # Wait, proper limit logic needed
            # For simplicity, if sigma ~ 0, use intrinsic of forwards
        # Just clamp sigma in caller usually, but here:
        sigma = 1e-9

    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    
    if option_type == "call":
        price = S * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        price = K * math.exp(-r * T) * norm_cdf(-d2) - S * math.exp(-q * T) * norm_cdf(-d1)
        
    return price

def bs_greeks(S, K, T, r, q, sigma, option_type="call"):
    """Computes Delta, Gamma, Vega, Theta, Rho."""
    if T <= 0:
        return {
            "delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0
        }
    
    if sigma < 1e-9: sigma = 1e-9

    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    nd1 = norm_pdf(d1)
    
    # Common terms
    exp_qT = math.exp(-q * T)
    exp_rT = math.exp(-r * T)
    sqrt_T = math.sqrt(T)
    
    # Gamma (same for call and put)
    gamma = (exp_qT * nd1) / (S * sigma * sqrt_T)
    
    # Vega (same for call and put) - raw derivative dV/dSigma
    vega = S * exp_qT * nd1 * sqrt_T
    
    if option_type == "call":
        delta = exp_qT * norm_cdf(d1)
        rho = K * T * exp_rT * norm_cdf(d2)
        theta = (- (S * exp_qT * nd1 * sigma) / (2 * sqrt_T) 
                 - r * K * exp_rT * norm_cdf(d2) 
                 + q * S * exp_qT * norm_cdf(d1))
    else: # put
        delta = -exp_qT * norm_cdf(-d1)
        rho = -K * T * exp_rT * norm_cdf(-d2)
        theta = (- (S * exp_qT * nd1 * sigma) / (2 * sqrt_T) 
                 + r * K * exp_rT * norm_cdf(-d2) 
                 - q * S * exp_qT * norm_cdf(-d1))
                 
    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega / 100.0, # Display per 1% vol
        "theta": theta / 365.0, # Display per day usually? Request says "Theta output in per year with optional conversion". 
                                # I will store/return per Year in core, let UI/API handle conversion? 
                                # Prompt says: "Theta output in “per year” with an optional conversion to “per day” flag controlled from UI"
                                # So I should return Per Year and let frontend or API layer scale it.
                                # Wait, I'll return both in the API if needed.
                                # But standard Greek Theta definition is per year. 
                                # Let's return raw per year here.
        "rho": rho / 100.0 # Display per 1% rate
    }

def get_theta_raw(S, K, T, r, q, sigma, option_type="call"):
    # Return strict per-year theta for consistency with logic
    g = bs_greeks(S, K, T, r, q, sigma, option_type)
    return g["theta"] * 365.0 # Because I divided by 365 above.
    
# Actually, let's just make bs_greeks return STANDARD definitions (per unit time = year, per unit vol = 1.0)
# And I will handle scaling in the compute layer.
def bs_greeks_raw(S, K, T, r, q, sigma, option_type="call"):
    if T <= 1e-7:
        return { "delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0 }
    
    if sigma < 1e-9: sigma = 1e-9
    
    d1, d2 = d1_d2(S, K, T, r, q, sigma)
    nd1 = norm_pdf(d1)
    exp_qT = math.exp(-q * T)
    exp_rT = math.exp(-r * T)
    sqrt_T = math.sqrt(T)
    
    gamma = (exp_qT * nd1) / (S * sigma * sqrt_T)
    vega = S * exp_qT * nd1 * sqrt_T
    
    if option_type == "call":
        delta = exp_qT * norm_cdf(d1)
        rho = K * T * exp_rT * norm_cdf(d2)
        theta = (- (S * exp_qT * nd1 * sigma) / (2 * sqrt_T) 
                 - r * K * exp_rT * norm_cdf(d2) 
                 + q * S * exp_qT * norm_cdf(d1))
    else:
        delta = -exp_qT * norm_cdf(-d1)
        rho = -K * T * exp_rT * norm_cdf(-d2)
        theta = (- (S * exp_qT * nd1 * sigma) / (2 * sqrt_T) 
                 + r * K * exp_rT * norm_cdf(-d2) 
                 - q * S * exp_qT * norm_cdf(-d1))
    
    return {
        "delta": delta,
        "gamma": gamma,
        "vega": vega, 
        "theta": theta,
        "rho": rho
    }
