export interface BSLabSettings {
    tickers: [string, string, string];

    // Option Params (Shared Defaults or Per Ticker if override?)
    // We'll store per-ticker but UI can update all.
    params: Array<{
        S: number;
        K: number;
        sigma: number;
        r: number;
        q: number;
        option_type: 'call' | 'put';
        market_price?: number; // for IV
    }>;

    // Global Time Settings
    time: {
        mode: 'date' | 'years' | 'days';
        expiryDate: string; // ISO
        days: number;
        years: number;
        nowMode: 'system' | 'manual';
        manualNow: string; // ISO
    };

    // Heatmap Settings
    heatmap: {
        metric: string;
        xVar: string;
        yVar: string;
        xRange: { min: number; max: number; steps: number };
        yRange: { min: number; max: number; steps: number };
        viewMode: 'three' | 'compare';
        scaleMode: 'independent' | 'shared';
    };

    persistence: {
        autosave: boolean;
    };
}

export const DEFAULT_SETTINGS: BSLabSettings = {
    tickers: ["AAPL", "MSFT", "NVDA"],
    params: [
        { S: 100, K: 100, sigma: 0.2, r: 0.05, q: 0.0, option_type: 'call' },
        { S: 100, K: 100, sigma: 0.2, r: 0.05, q: 0.0, option_type: 'call' },
        { S: 100, K: 100, sigma: 0.2, r: 0.05, q: 0.0, option_type: 'call' }
    ],
    time: {
        mode: 'days',
        expiryDate: new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString().split('T')[0] + 'T16:00',
        days: 30,
        years: 30 / 365,
        nowMode: 'system',
        manualNow: new Date().toISOString()
    },
    heatmap: {
        metric: 'Call Price',
        xVar: 'S',
        yVar: 'sigma',
        xRange: { min: 80, max: 120, steps: 20 },
        yRange: { min: 0.1, max: 0.5, steps: 20 },
        viewMode: 'three',
        scaleMode: 'shared'
    },
    persistence: {
        autosave: true
    }
};

export interface ComputeResult {
    tickers: Array<{
        ticker: string;
        call: number;
        put: number;
        delta: number;
        gamma: number;
        vega: number;
        theta: number;
        rho: number;
        iv?: number;
        iv_status?: string;
    }>;
    heatmap?: Array<{
        xValues: number[];
        yValues: number[];
        zMatrix: number[][];
    }>;
    error?: string;
}
