document.addEventListener('DOMContentLoaded', function () {
    // --- VARIÁVEIS GLOBAIS E ELEMENTOS DO DOM ---
    const loadingSpinner = document.getElementById('loading-spinner');
    const searchTermInput = document.getElementById('search-term');
    const datePickerInput = document.getElementById('date-range-picker');
    const tipoSelect = document.getElementById('tipo');
    const categoriaSelect = document.getElementById('categoria');
    const btnMesAtual = document.getElementById('btn-mes-atual');
    const btnAnoAtual = document.getElementById('btn-ano-atual');
    const paginationControls = document.getElementById('pagination-controls');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    const pageInfo = document.getElementById('page-info');

    let debounceTimeout;
    let currentPage = 1;

    // --- FUNÇÃO DE FORMATAÇÃO DE MOEDA ---
    const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

    // --- FUNÇÕES DE ATUALIZAÇÃO DA UI ---
    function atualizarTabela(transacoes) {
        const corpoTabela = document.getElementById('tabela-transacoes-corpo');
        corpoTabela.innerHTML = '';
        if (transacoes.length === 0) {
            corpoTabela.innerHTML = '<tr><td colspan="6" class="text-center text-muted p-4">Nenhuma transação encontrada para os filtros selecionados.</td></tr>';
            return;
        }
        transacoes.forEach(t => {
            const acoesHtml = t.is_skipped ?
                `<form action="/transacoes/reativar" method="post" class="d-inline" onsubmit="return confirm('Deseja reativar esta ocorrência?');">
                    <input type="hidden" name="csrf_token" value="${t.csrf_token}"/>
                    <input type="hidden" name="transacao_id" value="${t.id}">
                    <input type="hidden" name="data_excecao" value="${t.data_iso}">
                    <button type="submit" class="btn btn-sm btn-outline-success" title="Reativar"><i class="bi bi-calendar-check"></i></button>
                 </form>`
                :
                `<button type="button" class="btn btn-sm btn-outline-warning edit-btn" title="Editar" data-dados='${JSON.stringify(t)}'><i class="bi bi-pencil-square"></i></button>
                 ${t.recorrencia ? 
                    `<form action="/transacoes/excluir/${t.id}" method="post" class="d-inline" onsubmit="return confirm('Apagar a regra e TODAS as suas ocorrências futuras?');">
                        <input type="hidden" name="csrf_token" value="${t.csrf_token}"/>
                        <button type="submit" class="btn btn-sm btn-outline-danger" title="Excluir Regra"><i class="bi bi-trash3"></i></button>
                     </form>
                     <form action="/transacoes/ignorar" method="post" class="d-inline" onsubmit="return confirm('Deseja ignorar apenas esta ocorrência?');">
                        <input type="hidden" name="csrf_token" value="${t.csrf_token}"/>
                        <input type="hidden" name="transacao_id" value="${t.id}">
                        <input type="hidden" name="data_excecao" value="${t.data_iso}">
                        <button type="submit" class="btn btn-sm btn-outline-secondary" title="Ignorar ocorrência"><i class="bi bi-calendar-x"></i></button>
                     </form>` 
                    : 
                    `<form action="/transacoes/excluir/${t.id}" method="post" class="d-inline" onsubmit="return confirm('Tem certeza?');">
                        <input type="hidden" name="csrf_token" value="${t.csrf_token}"/>
                        <button type="submit" class="btn btn-sm btn-outline-danger" title="Excluir"><i class="bi bi-trash3"></i></button>
                     </form>`
                 }`;

            corpoTabela.insertAdjacentHTML('beforeend', `
                <tr class="${t.is_skipped ? 'text-muted opacity-75 text-decoration-line-through' : ''}">
                    <td>${t.categoria_nome}</td>
                    <td><span class="badge rounded-pill ${t.tipo_badge_class}">${t.tipo}</span></td>
                    <td>${t.descricao} ${t.recorrencia && !t.is_skipped ? '<span class="ms-1 text-primary-emphasis fw-normal" title="Recorrente"><i class="bi bi-arrow-repeat"></i></span>' : ''}</td>
                    <td>${t.data_formatada}</td>
                    <td class="text-end fw-bold ${t.valor_class}">${t.valor_formatado}</td>
                    <td class="text-end">${acoesHtml}</td>
                </tr>`);
        });
    }

    function atualizarPaginacao(data) {
        if (!pageInfo) return;
        pageInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
        prevPageBtn.parentElement.classList.toggle('disabled', !data.has_prev);
        nextPageBtn.parentElement.classList.toggle('disabled', !data.has_next);
        prevPageBtn.dataset.page = data.prev_page;
        nextPageBtn.dataset.page = data.next_page;
        paginationControls.style.display = data.total_pages > 1 ? 'flex' : 'none';
    }

    async function atualizarTransacoes(page = 1) {
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        currentPage = page;
        const inicio = datePicker.getStartDate();
        const fim = datePicker.getEndDate();
        if (!inicio || !fim) { if (loadingSpinner) loadingSpinner.style.display = 'none'; return; }
        
        const params = new URLSearchParams({
            inicio: inicio.toJSDate().toISOString().split('T')[0],
            fim: fim.toJSDate().toISOString().split('T')[0],
            q: searchTermInput.value, 
            tipo: tipoSelect.value, 
            page: currentPage
        });
        
        // --- CORREÇÃO APLICADA AQUI ---
        // Lendo os valores de um <select multiple> padrão do navegador, sem TomSelect.
        const selectedCategories = Array.from(categoriaSelect.selectedOptions).map(opt => opt.value);
        selectedCategories.forEach(catId => {
            if (catId) params.append('categoria', catId);
        });
        
        const apiUrl = `/api/transacoes?${params.toString()}`;
        
        try {
            const response = await fetch(apiUrl);
            const data = await response.json();
            if (data.success) {
                atualizarTabela(data.transacoes);
                atualizarPaginacao(data);
            }
        } catch (error) { 
            console.error("Erro ao buscar dados:", error); 
        } finally { 
            if (loadingSpinner) loadingSpinner.style.display = 'none'; 
        }
    }

    // --- INICIALIZAÇÃO E EVENT LISTENERS ---
    
    // Listener de categoria agora é um listener padrão.
    categoriaSelect.addEventListener('change', () => atualizarTransacoes(1));
    
    const initialStartDate = new Date(datePickerInput.dataset.inicio + 'T00:00:00');
    const initialEndDate = new Date(datePickerInput.dataset.fim + 'T00:00:00');
    
    const datePicker = new Litepicker({
        element: datePickerInput, singleMode: false, format: 'DD/MM/YYYY', lang: 'pt-BR',
        startDate: initialStartDate, endDate: initialEndDate,
        dropdowns: { months: true, years: true },
        setup: (picker) => { picker.on('selected', () => { atualizarTransacoes(1); }); },
    });
    
    btnMesAtual.addEventListener('click', () => {
        const hoje = new Date();
        datePicker.setDateRange(new Date(hoje.getFullYear(), hoje.getMonth(), 1), new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0));
        atualizarTransacoes(1); 
    });
    
    btnAnoAtual.addEventListener('click', () => {
        const hoje = new Date();
        datePicker.setDateRange(new Date(hoje.getFullYear(), 0, 1), new Date(hoje.getFullYear(), 11, 31));
        atualizarTransacoes(1);
    });
    
    searchTermInput.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            if (searchTermInput.value.length === 0 || searchTermInput.value.length >= 2) {
                atualizarTransacoes(1);
            }
        }, 500);
    });
    
    tipoSelect.addEventListener('change', () => atualizarTransacoes(1));
    
    prevPageBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (!e.currentTarget.parentElement.classList.contains('disabled')) {
            atualizarTransacoes(parseInt(e.currentTarget.dataset.page));
        }
    });

    nextPageBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (!e.currentTarget.parentElement.classList.contains('disabled')) {
            atualizarTransacoes(parseInt(e.currentTarget.dataset.page));
        }
    });

    // Carrega os dados da primeira página ao iniciar
    atualizarTransacoes(1);
});