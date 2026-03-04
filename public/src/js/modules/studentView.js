function initProgressChart() {
    const canvas = document.getElementById('chart-progress');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const progressData = canvas.dataset.progress;

    if (!progressData) {
        canvas.parentElement.innerHTML = '<p style="color: var(--color-text-muted); text-align: center;">Geen data beschikbaar</p>';
        return;
    }

    const progressWithData = JSON.parse(progressData);
    const labels = progressWithData.map(item => item.title);
    const data = progressWithData.map(item => item.score_numeric);
    const scores = progressWithData.map(item => item.score);

    const backgroundColors = scores.map(score => {
        if (score === 'Sterk') return '#22c55e';
        if (score === 'Voldoende') return '#eab308';
        return '#ef4444';
    });

    if (labels.length === 0) {
        canvas.parentElement.innerHTML = '<p style="color: var(--color-text-muted); text-align: center;">Geen data beschikbaar</p>';
    } else {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Score (%)',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderRadius: 4,
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true, max: 100, ticks: { stepSize: 10 } }
                },
                responsive: true,
                plugins: { legend: { display: false } }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', initProgressChart);

