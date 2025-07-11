document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;

    const loadingSpinner = document.getElementById('loading-spinner');
    const datePickerInput = document.getElementById('date-range-picker');
    const pageUrl = window.location.pathname; 
    const apiEndpoint = pageUrl.replace('/view', '').replace('/analises', '/api/analises').replace('/transacoes', '/api/transacoes');
    
    const searchTermInput = filterForm.q;
    const tipoSelect = filterForm.tipo;
    const categoriaSelect = filterForm.categoria;
    const btnMesAtual = document.getElementById('btn-mes-atual');
    const btnAnoAtual = document.getElementById('btn-ano-atual');
    const paginationControls = document.getElementById('pagination-controls');
    const tableHeader = document.querySelector('table thead');
    
    let debounceTimeout;
    let tomSelect;
    let currentPage = 1;
    let currentSort = { by: 'data', order: 'desc' };

    function atualizarUICompleta(data) {
        if (document.getElementById('total-receitas-valor')) {
            document.getElementById('total-receitas-valor').textContent = data.total_receitas;
            document.getElementById('total-despesas-valor').textContent = data.total_despesas;
            document.getElementById('saldo-periodo-valor').textContent = data.saldo_periodo;
        }
        atualizarTabela(data.transacoes);
        atualizarPaginacao(data);
        updateSortIcons();
    }

    function atualizarTabela(transacoes) {
        const corpoTabela = document.getElementById('tabela-corpo');
        if (!corpoTabela) return;
        corpoTabela.innerHTML = '';
        if (transacoes.length === 0) {
            const colspan = corpoTabela.closest('table').querySelector('thead tr').childElementCount;
            corpoTabela.innerHTML = `<tr><td colspan="${colspan}" class="text-center text-muted p-4">Nenhuma transação encontrada.</td></tr>`;
            return;
        }
        transacoes.forEach(t => {
            let acoesHtml = '';
            if (pageUrl.includes('/transacoes')) {
                acoesHtml = t.is_skipped ?
                    `<form action="/transacoes/reativar" method="post" class="d-inline" onsubmit="return confirm('Deseja reativar esta ocorrência?');"><input type="hidden" name="csrf_token" value="${t.csrf_token}"/><input type="hidden" name="transacao_id" value="${t.id}"><input type="hidden" name="data_excecao" value="${t.data_iso}"><button type="submit" class="btn btn-sm btn-outline-success" title="Reativar"><i class="bi bi-calendar-check"></i></button></form>` :
                    `<button type="button" class="btn btn-sm btn-outline-warning edit-btn" title="Editar" data-dados='${JSON.stringify(t)}'><i class="bi bi-pencil-square"></i></button>
                     ${t.recorrencia ? `<form action="/transacoes/excluir/${t.id}" method="post" class="d-inline" onsubmit="return confirm('Apagar a regra e TODAS as suas ocorrências futuras?');"><input type="hidden" name="csrf_token" value="${t.csrf_token}"/><button type="submit" class="btn btn-sm btn-outline-danger" title="Excluir Regra"><i class="bi bi-trash3"></i></button></form><form action="/transacoes/ignorar" method="post" class="d-inline" onsubmit="return confirm('Deseja ignorar apenas esta ocorrência?');"><input type="hidden" name="csrf_token" value="${t.csrf_token}"/><input type="hidden" name="transacao_id" value="${t.id}"><input type="hidden" name="data_excecao" value="${t.data_iso}"><button type="submit" class="btn btn-sm btn-outline-secondary" title="Ignorar ocorrência"><i class="bi bi-calendar-x"></i></button></form>` : `<form action="/transacoes/excluir/${t.id}" method="post" class="d-inline" onsubmit="return confirm('Tem certeza?');"><input type="hidden" name="csrf_token" value="${t.csrf_token}"/><button type="submit" class="btn btn-sm btn-outline-danger" title="Excluir"><i class="bi bi-trash3"></i></button></form>`}`;
            }
            const linha = `
                <tr>
                    <td class="hide-on-mobile">${t.categoria_nome}</td>
                    <td><span class="badge rounded-pill ${t.tipo_badge_class}">${t.tipo}</span></td>
                    <td>${t.descricao} ${t.recorrencia && !t.is_skipped && pageUrl.includes('/transacoes') ? '<span class="ms-1 text-primary-emphasis fw-normal" title="Recorrente"><i class="bi bi-arrow-repeat"></i></span>' : ''}</td>
                    <td>${t.data_formatada}</td>
                    <td class="text-end fw-bold ${t.valor_class}">${t.valor_formatado}</td>
                    ${pageUrl.includes('/transacoes') ? `<td class="text-end">${acoesHtml}</td>` : ''}
                </tr>`;
            corpoTabela.insertAdjacentHTML('beforeend', linha);
        });
    }

    function atualizarPaginacao(data) {
        if (!paginationControls) return;
        const pageInfo = document.getElementById('page-info');
        const prevPageBtn = document.getElementById('prev-page-btn');
        const nextPageBtn = document.getElementById('next-page-btn');
        pageInfo.textContent = `Página ${data.current_page} de ${data.total_pages}`;
        prevPageBtn.parentElement.classList.toggle('disabled', !data.has_prev);
        nextPageBtn.parentElement.classList.toggle('disabled', !data.has_next);
        prevPageBtn.dataset.page = data.prev_page;
        nextPageBtn.dataset.page = data.next_page;
        paginationControls.style.display = data.total_pages > 1 ? 'flex' : 'none';
    }

    function updateSortIcons() {
        if (!tableHeader) return;
        tableHeader.querySelectorAll('.sortable-header').forEach(header => {
            const iconSpan = header.querySelector('.sort-icon');
            if (header.dataset.sortBy === currentSort.by) {
                header.classList.add('active');
                iconSpan.innerHTML = currentSort.order === 'asc' ? '<i class="bi bi-arrow-up"></i>' : '<i class="bi bi-arrow-down"></i>';
            } else {
                header.classList.remove('active');
                iconSpan.innerHTML = '';
            }
        });
    }

    async function atualizarFiltros(page = 1) {
        if (loadingSpinner) loadingSpinner.style.display = 'block';
        currentPage = page;
        const inicio = datePicker.getStartDate();
        const fim = datePicker.getEndDate();
        if (!inicio || !fim) { if (loadingSpinner) loadingSpinner.style.display = 'none'; return; }
        const params = new URLSearchParams({
            inicio: inicio.toJSDate().toISOString().split('T')[0],
            fim: fim.toJSDate().toISOString().split('T')[0],
            q: filterForm.q.value,
            tipo: filterForm.tipo.value,
            page: currentPage,
            sort_by: currentSort.by,
            order: currentSort.order
        });
        const selectedCategories = tomSelect.items;
        selectedCategories.forEach(catId => params.append('categoria', catId));
        const url = `${apiEndpoint}?${params.toString()}`;
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) { exportBtn.href = `/exportar/csv?${params.toString()}`; }
        try {
            const response = await fetch(url);
            const data = await response.json();
            if (data.success) {
                atualizarUICompleta(data);
            }
        } catch (error) { console.error("Erro ao buscar dados:", error); } 
        finally { if (loadingSpinner) loadingSpinner.style.display = 'none'; }
    }

    tomSelect = new TomSelect('#categoria', { plugins: ['remove_button'], placeholder: 'Todas' });
    const datePicker = new Litepicker({
        element: datePickerInput, singleMode: false, format: 'DD/MM/YYYY', lang: 'pt-BR',
        startDate: datePickerInput.dataset.inicio, endDate: datePickerInput.dataset.fim,
        dropdowns: { months: true, years: true },
        setup: (picker) => { picker.on('selected', () => { atualizarFiltros(1); }); },
    });

    filterForm.addEventListener('submit', (e) => { e.preventDefault(); atualizarFiltros(1); });
    tipoSelect.addEventListener('change', () => atualizarFiltros(1));
    tomSelect.on('change', () => atualizarFiltros(1));
    searchTermInput.addEventListener('input', () => {
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            if (searchTermInput.value.length === 0 || searchTermInput.value.length >= 2) {
                atualizarFiltros(1);
            }
        }, 500);
    });
    btnMesAtual?.addEventListener('click', () => {
        const hoje = new Date();
        datePicker.setDateRange(new Date(hoje.getFullYear(), hoje.getMonth(), 1), new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0));
        atualizarFiltros(1); 
    });
    btnAnoAtual?.addEventListener('click', () => {
        const hoje = new Date();
        datePicker.setDateRange(new Date(hoje.getFullYear(), 0, 1), new Date(hoje.getFullYear(), 11, 31));
        atualizarFiltros(1);
    });
    if (tableHeader) {
        tableHeader.addEventListener('click', (e) => {
            const header = e.target.closest('.sortable-header');
            if (!header) return;
            e.preventDefault();
            const sortBy = header.dataset.sortBy;
            if (currentSort.by === sortBy) {
                currentSort.order = currentSort.order === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.by = sortBy;
                currentSort.order = 'desc';
            }
            atualizarFiltros(1);
        });
    }
    document.getElementById('prev-page-btn')?.addEventListener('click', (e) => { e.preventDefault(); if (!e.currentTarget.parentElement.classList.contains('disabled')) { atualizarFiltros(parseInt(e.currentTarget.dataset.page)); } });
    document.getElementById('next-page-btn')?.addEventListener('click', (e) => { e.preventDefault(); if (!e.currentTarget.parentElement.classList.contains('disabled')) { atualizarFiltros(parseInt(e.currentTarget.dataset.page)); } });
    
    atualizarFiltros(1);
});