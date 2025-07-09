document.addEventListener('DOMContentLoaded', function () {
    const transactionModalEl = document.getElementById('transactionModal');
    if (!transactionModalEl) return;

    const modal = new bootstrap.Modal(transactionModalEl);
    const form = document.getElementById('transactionForm');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const addUrl = form.dataset.addUrl;
    const addCatUrl = form.dataset.addCatUrl;
    const sugerirUrl = form.dataset.sugerirUrl;
    
    let tomSelect;
    const selectCategoriaEl = document.getElementById('categoria_id');

    // Inicializa o TomSelect
    if (window.TomSelect && selectCategoriaEl) {
        tomSelect = new TomSelect(selectCategoriaEl, {
            plugins: ['remove_button'],
            placeholder: 'Selecione a categoria...'
        });
    }

    // LÓGICA DO FORMULÁRIO
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
    const recorrenciaSwitch = document.getElementById('recorrenciaSwitch');
    let valorMask;
    if (valorInput) { valorMask = IMask(valorInput, { mask: 'R$ num', blocks: { num: { mask: Number, scale: 2, thousandsSeparator: '.', padFractionalZeros: true, radix: ',', mapToRadix: ['.'] } } }); }
    if (recorrenciaSwitch) { recorrenciaSwitch.addEventListener('change', function() { document.getElementById('recorrencia-container').style.display = this.checked ? 'block' : 'none'; document.getElementById('recorrencia_switch_hidden_input').value = this.checked ? 'on' : 'off'; }); }
    
    // Lógica para ABRIR o modal de ADICIONAR
    document.getElementById('openAddModalBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        form.reset();
        modalLabel.textContent = 'Adicionar Transação';
        form.action = addUrl;
        if(valorMask) valorMask.unmaskedValue = '';
        document.getElementById('data').value = new Date().toISOString().split('T')[0];
        if(recorrenciaSwitch) { recorrenciaSwitch.checked = false; recorrenciaSwitch.dispatchEvent(new Event('change')); }
        if (tomSelect) { tomSelect.clear(); }
        modal.show();
    });

    // Lógica para ABRIR o modal de EDITAR (simplificada para teste)
    document.body.addEventListener('click', function(event) {
        const button = event.target.closest('.edit-btn');
        if (!button) return;

        form.reset();
        modalLabel.textContent = 'Editar Transação';
        const dados = JSON.parse(button.dataset.dados);
        form.action = `/transacoes/editar/${dados.id}`;
        form.querySelector('#edit-id').value = dados.id;
        document.getElementById('tipo').value = dados.tipo;
        if(valorMask) valorMask.unmaskedValue = String(dados.valor);
        document.getElementById('descricao').value = dados.descricao;
        document.getElementById('data').value = dados.data;
        document.getElementById('forma_pagamento').value = dados.forma_pagamento;
        if (recorrenciaSwitch) {
            recorrenciaSwitch.checked = !!dados.recorrencia;
            document.getElementById('recorrencia').value = dados.recorrencia || 'Mensal';
            document.getElementById('data_final_recorrencia').value = dados.data_final_recorrencia || '';
            recorrenciaSwitch.dispatchEvent(new Event('change'));
        }
        
        if (tomSelect) {
            // Apenas define o valor, sem filtrar as opções.
            tomSelect.setValue(String(dados.categoria_id));
        }
        
        modal.show();
    });

    // Lógica do modal de categoria rápida e outras continuam aqui...
    // ... (todo o resto do código que já estava correto)
    const addCategoryModalEl = document.getElementById('addCategoryModal');
    const openAddCategoryBtn = document.getElementById('openAddCategoryModalBtn');
    if (addCategoryModalEl && openAddCategoryBtn) {
        const addCategoryModal = new bootstrap.Modal(addCategoryModalEl);
        openAddCategoryBtn.addEventListener('click', (e) => { 
            e.stopPropagation(); 
            addCategoryModal.show(); 
        });
        
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
                    if (tomSelect) { 
                        tomSelect.addOption({
                            value: String(data.categoria.id), 
                            text: `${data.categoria.nome} (${data.categoria.tipo})`
                        }); 
                        tomSelect.setValue(String(data.categoria.id)); 
                    }
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
});