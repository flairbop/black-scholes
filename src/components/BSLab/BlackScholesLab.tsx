import React, { useState, useEffect, useCallback, useRef } from 'react';
import { type BSLabSettings, DEFAULT_SETTINGS, type ComputeResult } from './types';
import { settingsToParams, paramsToSettings, saveToLocal, loadFromLocal } from './utils';
import { SettingsPanel } from './SettingsPanel';
import { ResultsPanel } from './ResultsPanel';
import './BSLab.css';

export const BlackScholesLab: React.FC = () => {
    const [settings, setSettings] = useState<BSLabSettings>(DEFAULT_SETTINGS);
    const [results, setResults] = useState<ComputeResult | null>(null);
    const [loading, setLoading] = useState(false);

    // Ref to track if initial load happened to avoid overwriting URL/Local on first render
    const initialized = useRef(false);

    // Load state on mount
    useEffect(() => {
        const p = new URLSearchParams(window.location.search);
        if (p.has('data')) {
            const s = paramsToSettings(p);
            setSettings(s);
        } else {
            const local = loadFromLocal();
            if (local) setSettings(local);
        }
        initialized.current = true;
    }, []);

    // Compute Function
    const compute = useCallback(async (s: BSLabSettings) => {
        setLoading(true);
        try {
            // Prepare payload
            // Logic for "Time":
            // If mode is DATE, compute T from now.
            // If mode is DAYS/YEARS, use T directly.

            const now = s.time.nowMode === 'system' ? new Date() : new Date(s.time.manualNow);

            const finalParams = s.params.map(p => {
                let T = 0;
                if (s.time.mode === 'date') {
                    const expiry = new Date(s.time.expiryDate);
                    const diff = expiry.getTime() - now.getTime();
                    T = diff / (1000 * 3600 * 24 * 365.0); // Simple ACT/365
                } else if (s.time.mode === 'days') {
                    T = s.time.days / 365.0;
                } else {
                    T = s.time.years;
                }
                if (T < 0) T = 0;

                return {
                    ...p,
                    T,
                    // Ensure overrides
                    // K, sigma, r, q are typically shared in current UI implementation (SettingsPanel logic)
                    // But state has them.
                };
            });

            const payload = {
                tickers: s.tickers,
                params: finalParams,
                heatmap: s.heatmap
            };

            const res = await fetch('/api/compute', {
                method: 'POST',
                body: JSON.stringify(payload),
                headers: { 'Content-Type': 'application/json' }
            });

            if (!res.ok) {
                throw new Error(`Worker Error: ${res.statusText}`);
            }

            const data = await res.json();
            setResults(data);

        } catch (e: any) {
            setResults({ tickers: [], error: e.message });
        } finally {
            setLoading(false);
        }
    }, []);

    // Debounce Effect
    useEffect(() => {
        if (!initialized.current) return;

        // Persist
        saveToLocal(settings);

        // Compute debounce
        const t = setTimeout(() => {
            compute(settings);
        }, 200);

        return () => clearTimeout(t);
    }, [settings, compute]);

    // Share
    const onShare = () => {
        const p = settingsToParams(settings);
        const url = `${window.location.origin}${window.location.pathname}?${p.toString()}`;
        window.history.pushState({}, '', url);
        navigator.clipboard.writeText(url);
        alert("Link copied to clipboard!");
    };

    const onReset = () => {
        if (confirm("Reset to defaults?")) {
            setSettings(DEFAULT_SETTINGS);
        }
    };

    return (
        <div className="bs-container">
            <SettingsPanel
                settings={settings}
                onChange={setSettings}
                onReset={onReset}
                onShare={onShare}
                loading={loading}
            />
            <ResultsPanel results={results} settings={settings} />
        </div>
    );
};
