import { useApiHandler } from './apiHandler.js';
import { loadFragment } from './fragmentLoader.js';

let currentChart = null;

export async function loadStudentaverage(targetSelector, url, selectUrl) {

    await loadFragment(targetSelector, url, ({ target, data }) => {
        if (!data) return;

        initProgressChart(target, "bar");
        initSubjectSelect(target, selectUrl, "bar");
    });
}

export async function loadStudentProgress(targetSelector, url, selectUrl) {


    await loadFragment(targetSelector, url, ({ target, data }) => {
        if (!data) return;

        initProgressChart(target);
        initSubjectSelect(target, selectUrl);
    });
}

function initProgressChart(container, type) {
    const canvas = container.querySelector('#chart-progress-over-time');

    if (!canvas) return;

    const chartData = JSON.parse(canvas.dataset.chart);
    renderChart(canvas, chartData, type);
}

function renderChart(canvas, chartData, type = 'line') {
    if (!chartData || !chartData.datasets || chartData.datasets.length === 0) {
        canvas.style.display = 'none';
        const msg = canvas.parentElement.querySelector('[data-no-data]');
        if (!msg) {
            const p = document.createElement('p');
            p.setAttribute('data-no-data', '');
            p.style.color = 'var(--color-text-muted)';
            p.style.textAlign = 'center';
            p.textContent = 'Geen voortgangsdata beschikbaar.';
            canvas.parentElement.appendChild(p);
        }
        return;
    }

    canvas.style.display = '';
    const existing = canvas.parentElement.querySelector('[data-no-data]');
    if (existing) existing.remove();

    if (currentChart) currentChart.destroy();

    const allValues = chartData.datasets.flatMap(ds => ds.data.filter(v => v !== null));
    let yMin = 0;
    let yMax = 100;
    if (allValues.length > 0) {
        const dataMin = Math.min(...allValues);
        const dataMax = Math.max(...allValues);
        const range = dataMax - dataMin;
        const padding = range < 5 ? 5 : Math.ceil(range * 0.2);
        yMin = Math.max(0, Math.floor((dataMin - padding) / 5) * 5);
        yMax = Math.min(100, Math.ceil((dataMax + padding) / 5) * 5);
    }

    const ctx = canvas.getContext('2d');
    currentChart = new Chart(ctx, {
        type: type,
        data: {
            labels: chartData.labels,
            datasets: chartData.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            spanGaps: true,
            scales: {
                x: {
                    stacked: true,
                    title: type === 'bar' ? { display: true, text: 'Kennis' } : { display: true, text: 'Datum' }
                },
                y: {
                    stacked: false,
                    min: type === 'bar' ? 0 : yMin,
                    max: type === 'bar' ? 100 : yMax,
                    ticks: type === 'bar' ? { stepSize: 10 } : { stepSize: Math.max(1, Math.round((yMax - yMin) / 10)) },
                    title: { display: true, text: 'Score (%)' }
                }
            },
            
            plugins: {
                legend: { display: true, position: 'top' }
            }
        }
    });
}

function initSubjectSelect(container, selectUrl, type) {
    const select = container.querySelector('#subject-select');
    if (!select) return;

    select.addEventListener('change', async () => {
        const subjectId = select.value;
        const canvas = container.querySelector('#chart-progress-over-time');
        if (!canvas) return;

        if (!subjectId) {
            const chartData = JSON.parse(canvas.dataset.chart);
            renderChart(canvas, chartData, type);
            return;
        }

        const request = useApiHandler(`${selectUrl}/${subjectId}`);
        const { data, error } = await request.Get();

        if (error) return;
        if (data) renderChart(canvas, data, type);
    });
}
