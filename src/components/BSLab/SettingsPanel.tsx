import React from 'react';
import { type BSLabSettings } from './types';

interface Props {
    settings: BSLabSettings;
    onChange: (s: BSLabSettings) => void;
    onReset: () => void;
    onShare: () => void;
    loading: boolean;
}

export const SettingsPanel: React.FC<Props> = ({ settings, onChange, onReset, onShare, loading }) => {

    const updateTicker = (idx: number, val: string) => {
        const newTickers = [...settings.tickers] as [string, string, string];
        newTickers[idx] = val.toUpperCase().replace(/[^A-Z0-9.-]/g, '');
        onChange({ ...settings, tickers: newTickers });
    };

    const updateParam = (idx: number, field: string, val: any) => {
        const newParams = [...settings.params];
        newParams[idx] = { ...newParams[idx], [field]: val };
        onChange({ ...settings, params: newParams });
    };

    const updateSharedParam = (field: string, val: any) => {
        const newParams = settings.params.map(p => ({ ...p, [field]: val }));
        onChange({ ...settings, params: newParams });
    };

    const updateHeatmap = (field: string, val: any) => {
        onChange({ ...settings, heatmap: { ...settings.heatmap, [field]: val } });
    };

    // Helper for numeric inputs
    const NumInput = ({ value, onChange, label, step = "0.01", ...props }: any) => (
        <div className="bs-input-col">
            <label>{label}</label>
            <input
                type="number"
                step={step}
                value={value}
                onChange={e => onChange(parseFloat(e.target.value))}
                {...props}
            />
        </div>
    );

    return (
        <div className="bs-sidebar">
            <div className="bs-header">
                <h1>Black–Scholes Lab</h1>
                <p>Tune parameters & visualize.</p>
            </div>

            {/* Group 1: Tickers */}
            <div className="bs-group">
                <div className="bs-group-title">1. Tickers</div>
                <div className="bs-input-row">
                    {settings.tickers.map((t, i) => (
                        <div key={i} className="bs-input-col">
                            <input
                                type="text"
                                value={t}
                                onChange={e => updateTicker(i, e.target.value)}
                                placeholder={`T${i + 1}`}
                            />
                            {!t && <span className="error-text">Required</span>}
                        </div>
                    ))}
                </div>
            </div>

            {/* Group 2: Option Params */}
            <div className="bs-group">
                <div className="bs-group-title">2. Option Parameters</div>

                <div className="bs-input-row">
                    <button
                        className={settings.params[0].option_type === 'call' ? 'primary' : ''}
                        onClick={() => updateSharedParam('option_type', 'call')}
                        style={{ flex: 1 }}
                    >Call</button>
                    <button
                        className={settings.params[0].option_type === 'put' ? 'primary' : ''}
                        onClick={() => updateSharedParam('option_type', 'put')}
                        style={{ flex: 1 }}
                    >Put</button>
                </div>

                {/* Spot Inputs (Per Ticker) */}
                <label style={{ marginTop: '0.5rem' }}>Spot Prices (S)</label>
                <div className="bs-input-row">
                    {settings.tickers.map((t, i) => (
                        <input
                            key={i}
                            type="number"
                            value={settings.params[i].S}
                            onChange={e => updateParam(i, 'S', parseFloat(e.target.value))}
                            placeholder={`S ${t}`}
                        />
                    ))}
                </div>

                {/* Common Params */}
                <div className="bs-input-row">
                    <NumInput
                        label="Strike (K)"
                        title="Strike Price"
                        value={settings.params[0].K}
                        onChange={(v: number) => updateSharedParam('K', v)}
                    />
                    <NumInput
                        label="Vol (σ)"
                        title="Volatility (decimal, e.g. 0.2)"
                        value={settings.params[0].sigma}
                        step="0.01"
                        onChange={(v: number) => updateSharedParam('sigma', v)}
                    />
                </div>
                <div className="bs-input-row">
                    <NumInput
                        label="Rate (r)"
                        title="Risk-free Rate (decimal, e.g. 0.05)"
                        value={settings.params[0].r}
                        step="0.01"
                        onChange={(v: number) => updateSharedParam('r', v)}
                    />
                    <NumInput
                        label="Div (q)"
                        title="Dividend Yield (decimal)"
                        value={settings.params[0].q}
                        step="0.01"
                        onChange={(v: number) => updateSharedParam('q', v)}
                    />
                </div>
            </div>

            {/* Group 3: Time */}
            <div className="bs-group">
                <div className="bs-group-title">3. Expiry / Time</div>
                <div className="bs-input-row">
                    <select
                        value={settings.time.mode}
                        onChange={e => onChange({
                            ...settings,
                            time: { ...settings.time, mode: e.target.value as any }
                        })}
                    >
                        <option value="days">Time to Expiry (Days)</option>
                        <option value="years">Time to Expiry (Years)</option>
                        <option value="date">Target Expiry Date</option>
                    </select>
                </div>

                {settings.time.mode === 'date' ? (
                    <div className="bs-input-col">
                        <input
                            type="datetime-local"
                            value={settings.time.expiryDate}
                            onChange={e => onChange({
                                ...settings,
                                time: { ...settings.time, expiryDate: e.target.value }
                            })}
                        />
                    </div>
                ) : (
                    <div className="bs-input-row">
                        {settings.time.mode === 'days' ? (
                            <NumInput
                                label="Days"
                                value={settings.time.days}
                                onChange={(v: number) => onChange({
                                    ...settings,
                                    time: { ...settings.time, days: v }
                                })}
                            />
                        ) : (
                            <NumInput
                                label="Years"
                                value={settings.time.years}
                                onChange={(v: number) => onChange({
                                    ...settings,
                                    time: { ...settings.time, years: v }
                                })}
                            />
                        )}
                    </div>
                )}
            </div>

            {/* Group 4: Heatmap */}
            <div className="bs-group">
                <div className="bs-group-title">4. Heatmap Controls</div>
                <div className="bs-input-col">
                    <label>Metric</label>
                    <select
                        value={settings.heatmap.metric}
                        onChange={e => updateHeatmap('metric', e.target.value)}
                    >
                        {['Call Price', 'Put Price', 'PnL', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho'].map(m => (
                            <option key={m} value={m}>{m}</option>
                        ))}
                    </select>
                </div>
                <div className="bs-input-row">
                    <div className="bs-input-col">
                        <label>X Axis</label>
                        <select
                            value={settings.heatmap.xVar}
                            onChange={e => updateHeatmap('xVar', e.target.value)}
                        >
                            {['S', 'K', 'T', 'sigma', 'r'].map(v => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </div>
                    <div className="bs-input-col">
                        <label>Y Axis</label>
                        <select
                            value={settings.heatmap.yVar}
                            onChange={e => updateHeatmap('yVar', e.target.value)}
                        >
                            {['S', 'K', 'T', 'sigma', 'r'].map(v => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Ranges (Simplified for UI space) */}
                <button onClick={() => {
                    // Reset ranges Logic
                    onChange({
                        ...settings,
                        heatmap: {
                            ...settings.heatmap,
                            xRange: { min: 80, max: 120, steps: 20 },
                            yRange: { min: 0.1, max: 0.5, steps: 20 }
                        }
                    })
                }}>Reset Ranges</button>
            </div>

            {/* Group 5: View & Persistence */}
            <div className="bs-group">
                <div className="bs-group-title">Actions</div>
                <div className="bs-input-row">
                    <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <input
                            type="checkbox"
                            checked={settings.persistence.autosave}
                            onChange={e => onChange({ ...settings, persistence: { autosave: e.target.checked } })}
                        />
                        Autosave
                    </label>
                </div>

                <div className="bs-input-row">
                    <button onClick={onReset}>Reset</button>
                    <button onClick={onShare} className="primary">Copy Link</button>
                </div>

                {loading && <div style={{ color: 'var(--accent)' }}>Computing...</div>}
            </div>
        </div>
    );
};
