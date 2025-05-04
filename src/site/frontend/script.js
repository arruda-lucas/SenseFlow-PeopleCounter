document.addEventListener('DOMContentLoaded', async () => {
    // Configuração comum para os gráficos
    const chartConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            }
        }
    };

    // Elementos do DOM
    const currentCountElement = document.getElementById('currentCount');
    const todayCtx = document.getElementById('todayChart').getContext('2d');
    const lastHourCtx = document.getElementById('lastHourChart').getContext('2d');
    const smoothCtx = document.getElementById('smoothChart').getContext('2d');

    // Variáveis para os gráficos
    let todayChart, lastHourChart, smoothChart;

    // Conexão SSE para atualizações em tempo real
    const eventSource = new EventSource('/updates');
    
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Atualiza a contagem atual
        currentCountElement.textContent = data.current_count;
        
        // Atualiza os gráficos se necessário
        if (data.charts_updated) {
            updateCharts();
        }
    };

    eventSource.onerror = () => {
        console.error('Erro na conexão SSE. Tentando reconectar...');
        setTimeout(() => {
            new EventSource('/updates');
        }, 5000);
    };

    // Função para atualizar todos os gráficos
    async function updateCharts() {
        try {
            const [todayData, lastHourData] = await Promise.all([
                fetch('/today_hourly').then(res => res.json()),
                fetch('/last_hour').then(res => res.json())
            ]);

            // Atualiza o gráfico de fluxo por hora
            if (todayChart) {
                todayChart.data.labels = todayData.map(item => `${item[0]}:00`);
                todayChart.data.datasets[0].data = todayData.map(item => item[1]);
                todayChart.data.datasets[0].backgroundColor = todayData.map(item => 
                    item[1] >= 0 ? 'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)');
                todayChart.data.datasets[0].borderColor = todayData.map(item => 
                    item[1] >= 0 ? 'rgba(46, 204, 113, 1)' : 'rgba(231, 76, 60, 1)');
                todayChart.update();
            } else {
                createTodayChart(todayData);
            }

            // Atualiza o gráfico da última hora
            if (lastHourChart) {
                lastHourChart.data.labels = lastHourData.map(item => item[0]);
                lastHourChart.data.datasets[0].data = lastHourData.map(item => item[1]);
                lastHourChart.data.datasets[1].data = lastHourData.map(item => item[2]);
                lastHourChart.update();
            } else {
                createLastHourChart(lastHourData);
            }

            // Atualiza o gráfico de variação cumulativa
            if (smoothChart) {
                let runningTotal = 0;
                const cumulativeData = todayData.map(item => {
                    runningTotal += item[1];
                    return Math.max(0, runningTotal);
                });
                
                smoothChart.data.labels = todayData.map(item => `${item[0]}:00`);
                smoothChart.data.datasets[0].data = cumulativeData;
                smoothChart.update();
            } else {
                createSmoothChart(todayData);
            }

        } catch (error) {
            console.error('Erro ao atualizar gráficos:', error);
        }
    }

    // Funções para criar os gráficos inicialmente
    function createTodayChart(todayData) {
        todayChart = new Chart(todayCtx, {
            type: 'bar',
            data: {
                labels: todayData.map(item => `${item[0]}:00`),
                datasets: [{
                    label: 'Fluxo por Hora',
                    data: todayData.map(item => item[1]),
                    backgroundColor: todayData.map(item => 
                        item[1] >= 0 ? 'rgba(46, 204, 113, 0.7)' : 'rgba(231, 76, 60, 0.7)'),
                    borderColor: todayData.map(item => 
                        item[1] >= 0 ? 'rgba(46, 204, 113, 1)' : 'rgba(231, 76, 60, 1)'),
                    borderWidth: 1
                }]
            },
            options: chartConfig
        });
    }

    function createLastHourChart(lastHourData) {
        lastHourChart = new Chart(lastHourCtx, {
            type: 'line',
            data: {
                labels: lastHourData.map(item => item[0]),
                datasets: [
                    {
                        label: 'Entradas',
                        data: lastHourData.map(item => item[1]),
                        borderColor: 'rgba(46, 204, 113, 1)',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0
                    },
                    {
                        label: 'Saídas',
                        data: lastHourData.map(item => item[2]),
                        borderColor: 'rgba(231, 76, 60, 1)',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0
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
    }

    function createSmoothChart(todayData) {
        let runningTotal = 0;
        const cumulativeData = todayData.map(item => {
            runningTotal += item[1];
            return Math.max(0, runningTotal);
        });

        smoothChart = new Chart(smoothCtx, {
            type: 'line',
            data: {
                labels: todayData.map(item => `${item[0]}:00`),
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
    }

    // Carrega os dados iniciais
    updateCharts();
});