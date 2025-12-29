from .core import bs_price
from .greeks import bs_greeks
import math

def linspace(start, end, steps):
    if steps <= 1:
        # If range is single point or steps=1
        return [start]
    step = (end - start) / (steps - 1)
    return [start + i * step for i in range(steps)]

def compute_metric_value(metric, S, K, T, r, q, sigma, option_type, base_price=None):
    if metric == "Call Price":
        return bs_price(S, K, T, r, q, sigma, "call")
    elif metric == "Put Price":
        return bs_price(S, K, T, r, q, sigma, "put")
    elif metric == "PnL":
        # PnL requires comparison to a base price.
        # If metric is PnL, we usually mean [Current Option Price] - [Baseline Option Price]
        # Base Price must be passed in.
        curr = bs_price(S, K, T, r, q, sigma, option_type)
        if base_price is not None:
            return curr - base_price
        return 0.0

    # Greeks
    g = bs_greeks(S, K, T, r, q, sigma, option_type)
    
    if metric == "Delta": return g["delta"]
    if metric == "Gamma": return g["gamma"]
    if metric == "Vega": return g["vega"] / 100.0   # Display per 1% vol
    if metric == "Theta": return g["theta"] / 365.0 # Display per day
    if metric == "Rho": return g["rho"] / 100.0     # Display per 1% rate
    
    # IV in heatmap?
    if metric == "IV":
        # If we are plotting IV, we usually mean we are viewing the Vol Surface if sigma is not constant?
        # But here sigma is an input. If X/Y is not sigma, IV is just constant sigma input.
        # If X is sigma, then IV = X.
        # Simple identity for this lab setup.
        return sigma

    return 0.0

def generate_heatmap_grid(params, metric, x_var, y_var, x_range, y_range):
    """
    params: dict with S, K, T, r, q, sigma, option_type
    x_range, y_range: {min, max, steps}
    """
    x_steps = int(x_range['steps'])
    y_steps = int(y_range['steps'])
    
    # Safety Cap
    MAX_CELLS = 6400
    if x_steps * y_steps > MAX_CELLS:
        ratio = x_steps / y_steps
        new_y = int(math.sqrt(MAX_CELLS / ratio))
        new_x = int(ratio * new_y)
        x_steps = max(10, new_x)
        y_steps = max(10, new_y)
        
    x_vals = linspace(x_range['min'], x_range['max'], x_steps)
    y_vals = linspace(y_range['min'], y_range['max'], y_steps)
    
    # If metric is PnL, calculate base price once
    base_price = None
    if metric == "PnL":
        base_price = bs_price(params['S'], params['K'], params['T'], params['r'], params['q'], params['sigma'], params['option_type'])
    
    z_matrix = []
    
    # Pre-copy dict to avoid re-creation overhead in loop (shallow copy ok for primitives)
    p = params.copy()
    
    for y in y_vals:
        row = []
        p[y_var] = y
        for x in x_vals:
            p[x_var] = x
            
            # Compute
            val = compute_metric_value(metric, p['S'], p['K'], p['T'], p['r'], p['q'], p['sigma'], p['option_type'], base_price)
            row.append(val)
        z_matrix.append(row)
        
    return {
        "xValues": x_vals,
        "yValues": y_vals,
        "zMatrix": z_matrix
    }
