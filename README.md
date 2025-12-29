# Black-Scholes Lab

## Overview
A high-performance interactive option pricing laboratory running entirely on Cloudflare (Pages + Workers).
Features a Python-based compute engine (via Pyodide) running serverlessly in the browser/worker.

## How it Works
1. **Frontend**: React + TypeScript + ECharts. hosted on Cloudflare Pages.
2. **Compute**: Python logic (`py/bs_lab`) is bundled and executed inside a Cloudflare Pages Function (`functions/api/compute.ts`) using Pyodide (WASM).
3. **Math**: Standard Black-Scholes formulas, Greeks, Implied Volatility solver (Bisection method), and Vectorized Heatmap generation.

## Development

1. **Setup**:
   ```bash
   npm install
   ```

2. **Bundle Python**:
   ```bash
   node scripts/bundle-python.js
   ```

3. **Run**:
   ```bash
   npm run dev
   ```

## Python Logic
Located in `py/bs_lab`.
- `core.py`: Pricing & Greeks
- `iv.py`: Implied Volatility
- `heatmap.py`: Grid Generator
- `api.py`: JSON API Entrypoint

## Limitations
- Initial compute request takes a few seconds to load Pyodide WASM. Subsequent requests are fast if cached.
- Compute is stateless per request.
