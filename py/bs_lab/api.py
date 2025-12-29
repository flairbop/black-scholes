import json
from .core import bs_price, bs_greeks_raw, get_theta_raw
from .iv import implied_volatility
from .heatmap import generate_heatmap_grid, compute_metric_value

def validate_positive(val, name, allow_zero=False):
    if allow_zero:
        if val < 0: return 0.0
    else:
        if val <= 1e-9: return 1e-9
    return val

def run_compute(payload_json: str) -> str:
    try:
        data = json.loads(payload_json)
        
        tickers = data.get("tickers", ["T1", "T2", "T3"])
        params_list = data.get("params", [])
        heatmap_req = data.get("heatmap", None)
        
        results = {
            "tickers": []
        }
        
        # 1. Compute Output Cards
        for i, p in enumerate(params_list):
            # Validate
            S = validate_positive(p.get("S", 100), "S")
            K = validate_positive(p.get("K", 100), "K")
            T = validate_positive(p.get("T", 1.0), "T", allow_zero=True)
            sigma = validate_positive(p.get("sigma", 0.2), "sigma")
            r = p.get("r", 0.05)
            q = p.get("q", 0.0)
            opt_type = p.get("option_type", "call")
            
            # Prices
            call = bs_price(S, K, T, r, q, sigma, "call")
            put = bs_price(S, K, T, r, q, sigma, "put")
            
            # Greeks (metric dependent on option type)
            greeks = bs_greeks_raw(S, K, T, r, q, sigma, opt_type)
            
            # IV if market price provided
            iv_res = None
            mkt_price = p.get("market_price", None)
            if mkt_price is not None:
                iv_res = implied_volatility(mkt_price, S, K, T, r, q, opt_type)
                
            results["tickers"].append({
                "ticker": tickers[i] if i < len(tickers) else f"T{i+1}",
                "call": call,
                "put": put,
                "delta": greeks["delta"],
                "gamma": greeks["gamma"],
                "vega": greeks["vega"] / 100.0,
                "theta": greeks["theta"] / 365.0, # Daily
                "rho": greeks["rho"] / 100.0,
                "iv": iv_res["iv"] if iv_res else None,
                "iv_status": iv_res["status"] if iv_res else None
            })
            
        # 2. Compute Heatmap (for each ticker)
        if heatmap_req:
            metric = heatmap_req.get("metric", "Call Price")
            x_var = heatmap_req.get("xVar", "S")
            y_var = heatmap_req.get("yVar", "sigma")
            x_range = heatmap_req.get("xRange", {"min": 50, "max": 150, "steps": 20})
            y_range = heatmap_req.get("yRange", {"min": 0.1, "max": 0.5, "steps": 20})
            
            grids = []
            for i, p in enumerate(params_list):
                # We need to pass the FULL params for this ticker to the grid gen
                # which will substitute xVar and yVar
                grid_params = {
                    "S": validate_positive(p.get("S", 100), "S"),
                    "K": validate_positive(p.get("K", 100), "K"),
                    "T": validate_positive(p.get("T", 1.0), "T", allow_zero=True),
                    "r": p.get("r", 0.05),
                    "q": p.get("q", 0.0),
                    "sigma": validate_positive(p.get("sigma", 0.2), "sigma"),
                    "option_type": p.get("option_type", "call")
                }
                
                grid = generate_heatmap_grid(grid_params, metric, x_var, y_var, x_range, y_range)
                grids.append(grid)
                
            results["heatmap"] = grids
            
        return json.dumps(results)
        
    except Exception as e:
        return json.dumps({"error": str(e)})
