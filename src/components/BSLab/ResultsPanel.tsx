import React from 'react';
import ReactECharts from 'echarts-for-react';
import { type ComputeResult, type BSLabSettings } from './types';

interface Props {
    results: ComputeResult | null;
    settings: BSLabSettings;
}

export const ResultsPanel: React.FC<Props> = ({ results, settings }) => {
    if (!results) {
        return <div className="bs-main">Loading or No Data...</div>;
    }

    if (results.error) {
        return <div className="bs-main"><div className="error-text">Error: {results.error}</div></div>;
    }

    const downloadCSV = (gridIndex: number) => {
        if (!results.heatmap) return;
        const grid = results.heatmap[gridIndex];
        if (!grid) return;

        // Header: x values
        let csv = `Y / X,${grid.xValues.join(',')}\n`;
        // Rows: y val, z values
        grid.yValues.forEach((y, i) => {
            csv += `${y},${grid.zMatrix[i].join(',')}\n`;
        });

        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `heatmap_${settings.tickers[gridIndex]}_${settings.heatmap.metric}.csv`;
        a.click();
    };

    const getChartOption = (gridIndex: number) => {
        if (!results.heatmap) return {};
        const grid = results.heatmap[gridIndex];

        // ECharts heatmap requires data in [x, y, z] format
        // But x and y in echarts are indices or categories usually.
        // Better to use mapping.

        const data = [];
        for (let i = 0; i < grid.yValues.length; i++) {
            for (let j = 0; j < grid.xValues.length; j++) {
                // x column (j), y row (i), value
                data.push([
                    j, // x index
                    i, // y index
                    grid.zMatrix[i][j] // value
                ]);
            }
        }

        return {
            tooltip: {
                position: 'top',
                formatter: (params: any) => {
                    const x = grid.xValues[params.value[0]].toFixed(2);
                    const y = grid.yValues[params.value[1]].toFixed(2);
                    const z = params.value[2].toFixed(4);
                    return `${settings.heatmap.xVar}: ${x}<br/>${settings.heatmap.yVar}: ${y}<br/>${settings.heatmap.metric}: ${z}`;
                }
            },
            animation: false,
            grid: { top: 20, right: 10, bottom: 20, left: 40 },
            xAxis: {
                type: 'category',
                data: grid.xValues.map(v => typeof v === 'number' ? v.toFixed(2) : v),
                splitArea: { show: true }
            },
            yAxis: {
                type: 'category',
                data: grid.yValues.map(v => typeof v === 'number' ? v.toFixed(2) : v),
                splitArea: { show: true }
            },
            visualMap: {
                min: Math.min(...grid.zMatrix.flat()),
                max: Math.max(...grid.zMatrix.flat()),
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: 0,
                show: false // Hide to save space, colors suffice
            },
            series: [{
                type: 'heatmap',
                data: data,
                label: { show: false },
                itemStyle: {
                    emphasis: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' }
                }
            }]
        };
    };

    return (
        <div className="bs-main">
            {/* Output Cards */}
            <div className="bs-card-grid">
                {results.tickers.map((res, i) => (
                    <div key={i} className="bs-card">
                        <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: 'var(--accent)' }}>{res.ticker}</div>
                        <div className="bs-metric-grid">
                            <span className="bs-metric-label">Call</span> <span className="bs-metric-value">{res.call.toFixed(2)}</span>
                            <span className="bs-metric-label">Put</span> <span className="bs-metric-value">{res.put.toFixed(2)}</span>

                            <span className="bs-metric-label">Delta</span> <span className="bs-metric-value">{res.delta.toFixed(3)}</span>
                            <span className="bs-metric-label">Gamma</span> <span className="bs-metric-value">{res.gamma.toFixed(3)}</span>
                            <span className="bs-metric-label">Vega</span> <span className="bs-metric-value">{res.vega.toFixed(3)}</span>
                            <span className="bs-metric-label">Theta</span> <span className="bs-metric-value">{res.theta.toFixed(3)}</span>
                            <span className="bs-metric-label">Rho</span> <span className="bs-metric-value">{res.rho.toFixed(3)}</span>

                            {res.iv !== null && res.iv !== undefined && (
                                <>
                                    <span className="bs-metric-label">Imp Vol</span>
                                    <span className="bs-metric-value">{(res.iv * 100).toFixed(1)}%</span>
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Heatmaps */}
            <h3>{settings.heatmap.metric} Heatmap</h3>
            <div className="bs-card-grid">
                {settings.tickers.map((t, i) => (
                    <div key={i} className="bs-card" style={{ minHeight: '300px', display: 'flex', flexDirection: 'column' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span>{t}</span>
                            <button onClick={() => downloadCSV(i)} style={{ padding: '2px 6px', fontSize: '0.7rem' }}>CSV</button>
                        </div>
                        <div style={{ flex: 1 }}>
                            {results.heatmap && results.heatmap[i] ? (
                                <ReactECharts
                                    option={getChartOption(i)}
                                    style={{ height: '250px', width: '100%' }}
                                    opts={{ renderer: 'canvas' }} // SVG or Canvas
                                />
                            ) : (
                                <div style={{ textAlign: 'center', padding: '2rem' }}>No Heatmap Data</div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
