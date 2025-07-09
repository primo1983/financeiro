document.addEventListener('DOMContentLoaded', function () {
    // --- VARIÁVEIS GLOBAIS E ELEMENTOS DO DOM ---
    const loadingSpinner = document.getElementById('loading-spinner');
    const searchTermInput = document.getElementById('search-term');
    const datePickerInput = document.getElementById('date-range-picker');
    const tipoSelect = document.getElementById('tipo');
    const categoriaSelect = document.getElementById('categoria');
    const btnMesAtual = document.getElementById('btn-mes-atual');
    const btnAnoAtual = document.getElementById('btn-ano-atual');
    const exportBtn = document.getElementById('exportBtn');

    let graficoDespesas, graficoReceitas;
    let debounceTimeout;
    let tomSelect; 

    // --- FUNÇÃO DE FORMATAÇÃO DE MOEDA ---
    const currencyFormatter = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    });

    // --- FUNÇÕES DE ATUALIZAÇÃO DA UI ---
    function atualizarCards(data) {
        document.getElementById('total-receitas-valor').textContent = currencyFormatter.format(data.total_receitas);
        document.getElementById('total-despesas-valor').textContent = currencyFormatter.format(data.total_despesas);
        document.getElementById('saldo-periodo-valor').textContent = currencyFormatter.format(data.saldo_periodo);
    }

    function atualizarTabela(transacoes) {
        const corpoTabela = document.getElementById('tabela-transacoes-corpo');
        corpoTabela.innerHTML = '';
        if (transacoes.length === 0) {
            corpoTabela.innerHTML = '<tr><td colspan="5" class="text-center text-muted p-4">Nenhuma transação encontrada.</td></tr>';
            return;
        }
        transacoes.forEach(t => {
            corpoTabela.insertAdjacentHTML('beforeend', `
                <tr>
                    <td>${t.categoria_nome}</td>
                    <td><span class="badge rounded-pill ${t.tipo_badge_class}">${t.tipo}</span></td>
                    <td>${t.descricao}</td>
                    <td>${t.data}</td>
                    <td class="text-end fw-bold ${t.valor_class}">${currencyFormatter.format(t.valor)}</td>
                </tr>`);
        });
    }

    // --- FUNÇÃO PRINCIPAL DE FETCH ---
    async function atualizarAnalises() {
        if (loadingSpinner) loadingSpinner.style.display = 'block';

        const inicio = datePicker.getStartDate();
        const fim = datePicker.getEndDate();
        if (!inicio || !fim) {
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            return;
        }

        const params = new URLSearchParams({
            inicio: inicio.toJSDate().toISOString().split('T')[0],
            fim: fim.toJSDate().toISOString().split('T')[0],
            q: searchTermInput.value,
            tipo: tipoSelect.value
        });
        
        const selectedCategories = tomSelect.items;
        selectedCategories.forEach(catId => params.append('categoria', catId));

        const apiUrl = `/api/analises?${params.toString()}`;
        
        // DEBUG: Mostra no console do navegador a URL que será chamada
        console.log("URL da API chamada:", apiUrl);
        
        exportBtn.href = `/exportar/csv?${params.toString()}`;

        try {
            const response = await fetch(apiUrl);
            const data = await response.json();

            // DEBUG: Mostra no console do navegador os dados recebidos
            console.log("Dados recebidos da API:", data);

            if (data.success) {
                atualizarCards(data);
                atualizarTabela(data.transacoes);
            }
        } catch (error) {
            console.error("Erro ao buscar dados da análise:", error);
        } finally {
            if (loadingSpinner) loadingSpinner.style.display = 'none';
        }
    }

    // --- INICIALIZAÇÃO E EVENT LISTENERS ---
    if (window.TomSelect) {
        tomSelect = new TomSelect('#categoria', {
            plugins: ['remove_button'],
            placeholder: 'Selecione as categorias...'
        });
        tomSelect.on('change', atualizarAnalises);
    } else {
        categoriaSelect.addEventListener('change', atualizarAnalises);
    }
    
    const datePicker = new Litepicker({
        element: datePickerInput, singleMode: false, format: 'DD/MM/YYYY', lang: 'pt-BR',
        dropdowns: { months: true, years: true },
        setup: (picker) => {
            picker.on('selected', () => {
                atualizarAnalises();
            });
        },
    });

    btnMesAtual.addEventListener('click', () => {
        const hoje = new Date();
        const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
        const fimMes = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0);
        datePicker.setDateRange(inicioMes, fimMes);
    });

    btnAnoAtual.addEventListener('click', () => {
        const hoje = new Date();
        const inicioAno = new Date(hoje.getFullYear(), 0, 1);
        const fimAno = new Date(hoje.getFullYear(), 11, 31);
        datePicker.setDateRange(inicioAno, fimAno);
    });

    searchTermInput.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            if (searchTermInput.value.length === 0 || searchTermInput.value.length >= 2) {
                atualizarAnalises();
            }
        }, 500);
    });

    tipoSelect.addEventListener('change', atualizarAnalises);
});