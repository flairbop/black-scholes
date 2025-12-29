from .core import bs_price, bs_greeks_raw
from .iv import implied_volatility
import math

def linspace(start, end, steps):
    if steps <= 1:
        return [start]
    step = (end - start) / (steps - 1)
    return [start + i * step for i in range(steps)]

def compute_metric_value(metric, S, K, T, r, q, sigma, option_type, base_price=None):
    if metric == "Call Price":
        return bs_price(S, K, T, r, q, sigma, "call")
    elif metric == "Put Price":
        return bs_price(S, K, T, r, q, sigma, "put")
    elif metric == "PnL":
        # PnL is (Current Price - Base Price)
        # We need the current price based on option_type
        curr_price = bs_price(S, K, T, r, q, sigma, option_type)
        if base_price is None:
            return 0.0 # Should not happen if correctly called
        return curr_price - base_price
    
    # Greeks
    greeks = bs_greeks_raw(S, K, T, r, q, sigma, option_type)
    
    if metric == "Delta": return greeks["delta"]
    if metric == "Gamma": return greeks["gamma"]
    if metric == "Vega": return greeks["vega"] / 100.0   # Scale for display
    if metric == "Theta": return greeks["theta"] / 365.0 # Scale to daily for display? Prompt said "per year" but "optional conversion". 
                                                         # Let's return Daily for the Heatmap as it's more intuitive number, 
                                                         # OR keep Per Year but label it. 
                                                         # Let's stick to Per Year as getting small numbers in heatmap is annoying?
                                                         # Actually, traders look at Daily theta. 
                                                         # Prompt: "Theta output in “per year”..."
                                                         # Let's standardise: Heatmap sees what output cards see.
                                                         # I will use Per Year / 365.0 (Daily) because standard web labs usually show daily theta.
                                                         # Actually, let's just use raw from core (Year) / 365.0 = Daily.
                                                         # I'll stick to Daily Theta for UI visualization.
    if metric == "Rho": return greeks["rho"] / 100.0     # Scale for display
    
    if metric == "IV":
        # Solve for IV given the computed price? No, that's circular if we are computing FROM params.
        # Unless X or Y is NOT sigma, and we want to see IV?
        # If we are simulating "Effect of Spot and Time on... IV?" 
        # IV is an input parameter (sigma). So IV is constant unless X or Y is sigma.
        # If X is sigma, then IV = X.
        # If we are plotting IV, we usually mean "Implied Vol surface".
        # But here valid inputs are S, K, sigma...
        # If metric is IV, just return sigma.
        return sigma

    return 0.0

def generate_heatmap_grid(params, metric, x_var, y_var, x_range, y_range):
    """
    params: dict with S, K, T, r, q, sigma, option_type
    x_range, y_range: {min, max, steps}
    """
    x_steps = int(x_range['steps'])
    y_steps = int(y_range['steps'])
    
    # Cap steps
    if x_steps * y_steps > 6400:
        # Simple cap logic: keep aspect ratio? or just clamp?
        # User said "auto-cap steps to keep product <= 6400"
        ratio = x_steps / y_steps
        # new_x * new_y = 6400 => ratio * new_y^2 = 6400 => new_y = sqrt(6400/ratio)
        new_y = int(math.sqrt(6400 / ratio))
        new_x = int(ratio * new_y)
        x_steps = new_x
        y_steps = new_y
        
    x_vals = linspace(x_range['min'], x_range['max'], x_steps)
    y_vals = linspace(y_range['min'], y_range['max'], y_steps)
    
    # Pre-compute base price if metric is PnL
    base_price = None
    if metric == "PnL":
        base_price = bs_price(params['S'], params['K'], params['T'], params['r'], params['q'], params['sigma'], params['option_type'])
    
    z_matrix = []
    
    # Create working copy of params
    p = params.copy()
    
    for y in y_vals:
        row = []
        p[y_var] = y
        for x in x_vals:
            p[x_var] = x
            
            # Compute
            # Ensure safe inputs (e.g. T > 0)
            # Core functions handle T<=0, but S<0 might be issues? Core handles math.log(S/K).
            # If x_var is S and x is negative (unlikely from UI), we crash.
            # We assume range is valid positive.
            
            val = compute_metric_value(metric, p['S'], p['K'], p['T'], p['r'], p['q'], p['sigma'], p['option_type'], base_price)
            row.append(val)
        z_matrix.append(row)
        
    return {
        "xValues": x_vals,
        "yValues": y_vals,
        "zMatrix": z_matrix
    }
