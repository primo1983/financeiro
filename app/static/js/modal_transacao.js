document.addEventListener('DOMContentLoaded', function () {
    const transactionModalEl = document.getElementById('transactionModal');
    if (!transactionModalEl) return;

    const modal = new bootstrap.Modal(transactionModalEl);
    const form = document.getElementById('transactionForm');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const addUrl = form.dataset.addUrl;
    const addCatUrl = form.dataset.addCatUrl;
    const sugerirUrl = form.dataset.sugerirUrl;
    
    // --- LÓGICA DE CATEGORIAS ---
    function filtrarCategorias(tipoTransacao) {
        const selectCategoria = document.getElementById('categoria_id');
        if (!selectCategoria) return;
        
        let primeiraOpcaoVisivel = null;
        for (const option of selectCategoria.options) {
            if (!option.value) continue;
            
            const tipoCategoria = option.dataset.tipoCategoria;
            const deveSerVisivel = (tipoCategoria === 'Ambos' || tipoCategoria === tipoTransacao);
            
            option.style.display = deveSerVisivel ? '' : 'none';
            
            if (deveSerVisivel && !primeiraOpcaoVisivel) {
                primeiraOpcaoVisivel = option;
            }
        }
        
        if (selectCategoria.options[selectCategoria.selectedIndex]?.style.display === 'none') {
            selectCategoria.value = primeiraOpcaoVisivel ? primeiraOpcaoVisivel.value : '';
        }
    }

    // --- LÓGICA DO FORMULÁRIO ---
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const actionUrl = form.getAttribute('action');
        fetch(actionUrl, {
            method: 'POST', body: formData,
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json().then(data => ({ ok: response.ok, body: data })))
        .then(({ ok, body }) => {
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            if (ok && body.success) { window.location.reload(); } 
            else {
                for (const fieldName in body.errors) {
                    const field = form.querySelector(`[name="${fieldName}"]`);
                    if (field) { field.classList.add('is-invalid'); }
                }
            }
        }).catch(error => console.error('Erro de Fetch:', error));
    });

    const modalLabel = document.getElementById('modalLabel');
    const valorInput = document.getElementById('valor');
    // CORREÇÃO: Buscando pelo novo ID
    const tipoSelect = document.getElementById('modal_tipo');
    const recorrenciaSwitch = document.getElementById('recorrenciaSwitch');
    let valorMask;
    if (valorInput) { valorMask = IMask(valorInput, { mask: 'R$ num', blocks: { num: { mask: Number, scale: 2, thousandsSeparator: '.', padFractionalZeros: true, radix: ',', mapToRadix: ['.'] } } }); }
    if (recorrenciaSwitch) { recorrenciaSwitch.addEventListener('change', function() { document.getElementById('recorrencia-container').style.display = this.checked ? 'block' : 'none'; document.getElementById('recorrencia_switch_hidden_input').value = this.checked ? 'on' : 'off'; }); }
    
    // Agora o listener será anexado ao elemento correto
    if (tipoSelect) { tipoSelect.addEventListener('change', () => filtrarCategorias(tipoSelect.value)); }

    // Lógica para ABRIR o modal de ADICIONAR
    document.getElementById('openAddModalBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        form.reset();
        modalLabel.textContent = 'Adicionar Transação';
        form.action = addUrl;
        if(valorMask) valorMask.unmaskedValue = '';
        document.getElementById('data').value = new Date().toISOString().split('T')[0];
        
        const tipoPadrao = 'Despesa';
        if(tipoSelect) tipoSelect.value = tipoPadrao;
        filtrarCategorias(tipoPadrao);

        if(recorrenciaSwitch) { 
            recorrenciaSwitch.checked = false; 
            recorrenciaSwitch.dispatchEvent(new Event('change')); 
        }
        modal.show();
    });

    // Lógica para ABRIR o modal de EDITAR
    document.body.addEventListener('click', function(event) {
        const button = event.target.closest('.edit-btn');
        if (!button) return;

        form.reset();
        modalLabel.textContent = 'Editar Transação';
        const dados = JSON.parse(button.dataset.dados);
        
        form.action = `/transacoes/editar/${dados.id}`;
        form.querySelector('#edit-id').value = dados.id;
        if(tipoSelect) tipoSelect.value = dados.tipo;
        if(valorMask) { valorMask.unmaskedValue = String(dados.valor); }
        document.getElementById('descricao').value = dados.descricao;
        document.getElementById('data').value = dados.data;
        document.getElementById('forma_pagamento').value = dados.forma_pagamento;
        if (recorrenciaSwitch) {
            recorrenciaSwitch.checked = !!dados.recorrencia;
            document.getElementById('recorrencia').value = dados.recorrencia || 'Mensal';
            document.getElementById('data_final_recorrencia').value = dados.data_final_recorrencia || '';
            recorrenciaSwitch.dispatchEvent(new Event('change'));
        }
        
        filtrarCategorias(dados.tipo);
        document.getElementById('categoria_id').value = dados.categoria_id;
        
        modal.show();
    });

    // Lógica do modal de categoria rápida (sem alterações)
    const addCategoryModalEl = document.getElementById('addCategoryModal');
    const openAddCategoryBtn = document.getElementById('openAddCategoryModalBtn');
    if (addCategoryModalEl && openAddCategoryBtn) {
        const addCategoryModal = new bootstrap.Modal(addCategoryModalEl);
        openAddCategoryBtn.addEventListener('click', (e) => { e.stopPropagation(); addCategoryModal.show(); });
        const addCategoryForm = document.getElementById('addCategoryForm');
        addCategoryForm.addEventListener('submit', function(e) { 
            e.preventDefault();
            const nomeInput = document.getElementById('quick_cat_nome');
            const tipoInput = document.getElementById('quick_cat_tipo');
            nomeInput.classList.remove('is-invalid');
            fetch(addCatUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ nome: nomeInput.value, tipo: tipoInput.value })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const selectCategoria = document.getElementById('categoria_id');
                    const newOption = new Option(`${data.categoria.nome} (${data.categoria.tipo})`, data.categoria.id);
                    newOption.dataset.tipoCategoria = data.categoria.tipo;
                    selectCategoria.add(newOption);
                    selectCategoria.value = data.categoria.id;
                    addCategoryModal.hide();
                    this.reset();
                } else {
                    for (const fieldName in data.errors) {
                        const field = addCategoryForm.querySelector(`[name="${fieldName}"]`);
                        if (field) { field.classList.add('is-invalid'); }
                    }
                }
            });
        });
    }

    // Lógica do lançamento inteligente (sem alterações)
    let debounceTimeout;
    const descricaoInput = document.getElementById('descricao');
    if (descricaoInput) {
        descricaoInput.addEventListener('input', function() {
            clearTimeout(debounceTimeout);
            const searchTerm = this.value;
            if (searchTerm.length < 3) { return; }
            debounceTimeout = setTimeout(() => {
                fetch(sugerirUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify({ descricao: searchTerm })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.sugestao_categoria_id) {
                         document.getElementById('categoria_id').value = data.sugestao_categoria_id;
                    }
                    if (data.sugestao_forma_pagamento) { 
                        document.getElementById('forma_pagamento').value = data.sugestao_forma_pagamento; 
                    }
                });
            }, 500);
        });
    }
});