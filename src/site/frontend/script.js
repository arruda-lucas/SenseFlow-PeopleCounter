document.addEventListener('DOMContentLoaded', async () => {
    async function updateCurrentCount() {
        try {
            const response = await fetch('/current_count');
            const data = await response.json();
            document.getElementById('currentCount').textContent = data.count;
        } catch (error) {
            console.error('Erro ao atualizar contagem:', error);
        }
    }

    const chartConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            }
        }
    };

    // 1. Fluxo por Hora
    const todayCtx = document.getElementById('todayChart').getContext('2d');
    const todayData = await (await fetch('/today_hourly')).json();
    const todayLabels = todayData.map(item => `${item[0]}:00`);
    const todayValues = todayData.map(item => item[1]);

    new Chart(todayCtx, {
        type: 'bar',
        data: {
            labels: todayLabels,
            datasets: [{
                label: 'Fluxo por Hora',
                data: todayValues,
                backgroundColor: todayValues.map(value => value >= 0 ? 'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)'),
                borderColor: todayValues.map(value => value >= 0 ? 'rgba(46, 204, 113, 1)' : 'rgba(231, 76, 60, 1)'),
                borderWidth: 1
            }]
        },
        options: chartConfig
    });

    // 2. Última Hora (Entradas e Saídas) - Versão Atualizada
    const lastHourCtx = document.getElementById('lastHourChart').getContext('2d');
    const lastHourData = await (await fetch('/last_hour')).json();

    // Extrai os dados
    const lastHourLabels = lastHourData.map(item => item[0]);
    const entriesData = lastHourData.map(item => item[1]);
    const exitsData = lastHourData.map(item => item[2]);

    new Chart(lastHourCtx, {
        type: 'line',
        data: {
            labels: lastHourLabels,
            datasets: [
                {
                    label: 'Entradas',
                    data: entriesData,
                    borderColor: 'rgba(46, 204, 113, 1)',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,  // Linha suave
                    fill: true,
                    pointRadius: 0  // Remove os pontos para ficar mais limpo
                },
                {
                    label: 'Saídas',
                    data: exitsData,
                    borderColor: 'rgba(231, 76, 60, 1)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,  // Linha suave
                    fill: true,
                    pointRadius: 0  // Remove os pontos para ficar mais limpo
                }
            ]
        },
        options: {
            ...chartConfig,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Quantidade de Pessoas'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Horário'
                    }
                }
            }
        }
    });

    // 3. Variação do Dia (Cumulativo)
    const smoothCtx = document.getElementById('smoothChart').getContext('2d');
    let runningTotal = 0;
    const cumulativeData = todayData.map(item => {
        runningTotal += item[1];
        return Math.max(0, runningTotal);
    });

    new Chart(smoothCtx, {
        type: 'line',
        data: {
            labels: todayLabels,
            datasets: [{
                label: 'Variação do Dia',
                data: cumulativeData,
                borderColor: 'rgba(155, 89, 182, 1)',
                backgroundColor: 'rgba(155, 89, 182, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true
            }]
        },
        options: chartConfig
    });

    setInterval(updateCurrentCount, 3000);
    updateCurrentCount();
});
