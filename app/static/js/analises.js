document.addEventListener('DOMContentLoaded', function () {
    // --- LÓGICA DO FORMULÁRIO DE FILTRO ---
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const ano = document.getElementById('ano').value;
            const mes = document.getElementById('mes').value;
            const formData = new FormData(filterForm);
            formData.delete('ano');
            formData.delete('mes');
            const query = new URLSearchParams(formData).toString();
            
            const baseUrl = `/analises/${ano}/${mes}`;
            window.location.href = query ? `${baseUrl}?${query}` : baseUrl;
        });
    }

    // --- LÓGICA DOS GRÁFICOS ---
    const chartDataEl = document.getElementById('chart-data');
    if (!chartDataEl) return;
    
    const chartData = JSON.parse(chartDataEl.textContent);
    const chartColors = ['#0d6efd', '#6f42c1', '#198754', '#dc3545', '#ffc107', '#0dcaf0', '#d63384', '#fd7e14', '#20c997', '#6c757d'];

    // GRÁFICO DE PIZZA - DESPESAS
    const despesasPieCanvas = document.getElementById('graficoDespesas');
    if (despesasPieCanvas && chartData.despesasValores.length > 0) {
        new Chart(despesasPieCanvas, {
            type: 'pie',
            data: {
                labels: chartData.despesasLabels,
                datasets: [{ data: chartData.despesasValores, backgroundColor: chartColors }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }
    
    // GRÁFICO DE PIZZA - RECEITAS
    const receitasPieCanvas = document.getElementById('graficoReceitas');
    if (receitasPieCanvas && chartData.receitasValores.length > 0) {
        new Chart(receitasPieCanvas, {
            type: 'pie',
            data: {
                labels: chartData.receitasLabels,
                datasets: [{ data: chartData.receitasValores, backgroundColor: chartColors }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    }

    // GRÁFICO DE BARRAS - FLUXO DE CAIXA MENSAL
    const fluxoCanvas = document.getElementById('fluxoDeCaixaChart');
    if (fluxoCanvas && chartData.fluxoLabels.length > 0) {
        new Chart(fluxoCanvas, {
            type: 'bar',
            data: {
                labels: chartData.fluxoLabels,
                datasets: [
                    { label: 'Receitas', data: chartData.fluxoReceitas, backgroundColor: 'rgba(25, 135, 84, 0.7)' },
                    { label: 'Despesas', data: chartData.fluxoDespesas, backgroundColor: 'rgba(220, 53, 69, 0.7)' }
                ]
            },
            options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } }
        });
    }
});