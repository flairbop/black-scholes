import json
from .core import bs_price
from .greeks import bs_greeks
from .iv import implied_volatility
from .heatmap import generate_heatmap_grid

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
            try:
                # Validation
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
                
                # Greeks
                greeks = bs_greeks(S, K, T, r, q, sigma, opt_type)
                
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
                    "vega": greeks["vega"] / 100.0, # Scale for display
                    "theta": greeks["theta"] / 365.0, # Scale to Daily
                    "rho": greeks["rho"] / 100.0, # Scale
                    "iv": iv_res["iv"] if iv_res else None,
                    "iv_status": iv_res["status"] if iv_res else None
                })
            except Exception as e:
                # Per ticker error fallback
                results["tickers"].append({
                    "ticker": tickers[i] if i < len(tickers) else f"T{i+1}",
                    "error": str(e),
                    # Zero defaults to not break UI typings
                    "call": 0, "put": 0, "delta": 0, "gamma": 0, "vega": 0, "theta": 0, "rho": 0
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
                try:
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
                except Exception as e:
                     # Add empty grid or error indicator
                     grids.append({"error": str(e), "xValues": [], "yValues": [], "zMatrix": []})
                
            results["heatmap"] = grids
            
        return json.dumps(results)
        
    except Exception as e:
        return json.dumps({"error": f"Top level error: {str(e)}"})
