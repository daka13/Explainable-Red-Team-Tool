/**
 * Charts Module - Plotly Visualizations
 */

class Charts {
    static plotRefusalRateByModel(results) {
        const grouped = {};
        results.forEach(r => {
            if (!grouped[r.model]) grouped[r.model] = { refused: 0, total: 0 };
            grouped[r.model].total++;
            if (r.refused) grouped[r.model].refused++;
        });

        const data = [{
            x: Object.keys(grouped),
            y: Object.values(grouped).map(g => (g.refused / g.total) * 100),
            type: 'bar',
            marker: {
                color: Object.values(grouped).map(g => (g.refused / g.total) * 100),
                colorscale: [[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                line: { width: 0 }
            },
            text: Object.values(grouped).map(g => `${((g.refused / g.total) * 100).toFixed(1)}%`),
            textposition: 'outside'
        }];

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#E6F1FF', family: 'Inter' },
            yaxis: { title: 'Refusal Rate (%)', gridcolor: 'rgba(255,255,255,0.1)' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            margin: { t: 20, b: 60, l: 60, r: 20 },
            height: 300
        };

        Plotly.newPlot('refusalRateChart', data, layout, { responsive: true, displayModeBar: false });
    }

    static plotLatency(results) {
        const byModel = {};
        results.forEach(r => {
            if (!byModel[r.model]) byModel[r.model] = [];
            byModel[r.model].push(r.latency_ms);
        });

        const data = Object.entries(byModel).map(([model, latencies]) => ({
            y: latencies,
            name: model,
            type: 'box',
            boxmean: 'sd'
        }));

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#E6F1FF', family: 'Inter' },
            yaxis: { title: 'Latency (ms)', gridcolor: 'rgba(255,255,255,0.1)' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            margin: { t: 20, b: 60, l: 60, r: 20 },
            height: 300,
            showlegend: false
        };

        Plotly.newPlot('latencyChart', data, layout, { responsive: true, displayModeBar: false });
    }

    static plotCategoryHeatmap(results) {
        const models = [...new Set(results.map(r => r.model))];
        const categories = [...new Set(results.map(r => r.prompt_category))];

        const matrix = categories.map(cat =>
            models.map(model => {
                const filtered = results.filter(r => r.model === model && r.prompt_category === cat);
                if (filtered.length === 0) return null;
                return (filtered.filter(r => r.refused).length / filtered.length) * 100;
            })
        );

        const data = [{
            z: matrix,
            x: models,
            y: categories,
            type: 'heatmap',
            colorscale: [[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
            showscale: true
        }];

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#E6F1FF', family: 'Inter' },
            margin: { t: 40, b: 100, l: 120, r: 20 },
            height: 400
        };

        Plotly.newPlot('heatmapChart', data, layout, { responsive: true, displayModeBar: false });
    }

    static plotSuccessRateByCategory(results) {
        const byCategory = {};
        results.forEach(r => {
            if (!byCategory[r.prompt_category]) byCategory[r.prompt_category] = {};
            if (!byCategory[r.prompt_category][r.model]) {
                byCategory[r.prompt_category][r.model] = { refused: 0, total: 0 };
            }
            byCategory[r.prompt_category][r.model].total++;
            if (!r.refused) byCategory[r.prompt_category][r.model].refused++;
        });

        const models = [...new Set(results.map(r => r.model))];
        const data = models.map(model => ({
            x: Object.keys(byCategory),
            y: Object.keys(byCategory).map(cat => {
                const stats = byCategory[cat][model];
                return stats ? (stats.refused / stats.total) * 100 : 0;
            }),
            name: model,
            type: 'bar'
        }));

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#E6F1FF', family: 'Inter' },
            yaxis: { title: 'Success Rate (%)', gridcolor: 'rgba(255,255,255,0.1)' },
            xaxis: { gridcolor: 'rgba(255,255,255,0.1)' },
            barmode: 'group',
            margin: { t: 20, b: 100, l: 60, r: 20 },
            height: 350
        };

        Plotly.newPlot('successRateChart', data, layout, { responsive: true, displayModeBar: false });
    }

    static plotVulnerabilityRadar(results) {
        const models = [...new Set(results.map(r => r.model))];
        const categories = [...new Set(results.map(r => r.prompt_category))];

        const data = models.map(model => {
            const values = categories.map(cat => {
                const filtered = results.filter(r => r.model === model && r.prompt_category === cat);
                if (filtered.length === 0) return 0;
                return ((filtered.filter(r => !r.refused).length / filtered.length) * 100);
            });
            values.push(values[0]); // Close the radar

            return {
                type: 'scatterpolar',
                r: values,
                theta: [...categories, categories[0]],
                fill: 'toself',
                name: model
            };
        });

        const layout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#E6F1FF', family: 'Inter' },
            polar: {
                radialaxis: { visible: true, range: [0, 100], gridcolor: 'rgba(255,255,255,0.2)' },
                angularaxis: { gridcolor: 'rgba(255,255,255,0.2)' }
            },
            margin: { t: 40, b: 40, l: 60, r: 60 },
            height: 400
        };

        Plotly.newPlot('radarChart', data, layout, { responsive: true, displayModeBar: false });
    }
}

window.Charts = Charts;
