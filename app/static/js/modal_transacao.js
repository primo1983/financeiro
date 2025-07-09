document.addEventListener('DOMContentLoaded', function () {
    const transactionModalEl = document.getElementById('transactionModal');
    if (!transactionModalEl) return;

    const modal = new bootstrap.Modal(transactionModalEl);
    const form = document.getElementById('transactionForm');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Pega as URLs dos atributos data-* do formulário
    const addUrl = form.dataset.addUrl;
    const addCatUrl = form.dataset.addCatUrl;
    const sugerirUrl = form.dataset.sugerirUrl;
    
    // LÓGICA DE ENVIO DO FORMULÁRIO PRINCIPAL COM AJAX
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const actionUrl = form.getAttribute('action');
        
        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json().then(data => ({ ok: response.ok, body: data })))
        .then(({ ok, body }) => {
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            if (ok && body.success) {
                window.location.reload();
            } else {
                for (const fieldName in body.errors) {
                    const field = form.querySelector(`[name="${fieldName}"]`);
                    if (field) { 
                        field.classList.add('is-invalid');
                    }
                }
            }
        }).catch(error => {
            console.error('Erro de Fetch:', error);
            alert('Ocorreu um erro de comunicação com o servidor.');
        });
    });

    // Inicialização de variáveis e máscaras
    const modalLabel = document.getElementById('modalLabel');
    const valorInput = document.getElementById('valor');
    let valorMask;
    if (valorInput) {
        valorMask = IMask(valorInput, {
            mask: 'R$ num',
            blocks: {
                num: { mask: Number, scale: 2, thousandsSeparator: '.', padFractionalZeros: true, radix: ',', mapToRadix: ['.'] }
            }
        });
    }
    
    // Lógica do switch de recorrência
    const recorrenciaSwitch = document.getElementById('recorrenciaSwitch');
    const hiddenRecorrenciaSwitch = document.getElementById('recorrencia_switch_hidden_input');
    if (recorrenciaSwitch && hiddenRecorrenciaSwitch) {
        recorrenciaSwitch.addEventListener('change', function() {
            const container = document.getElementById('recorrencia-container');
            hiddenRecorrenciaSwitch.value = this.checked ? 'on' : 'off';
            if(container) container.style.display = this.checked ? 'block' : 'none';
            if (!this.checked) {
                document.getElementById('recorrencia').value = 'Mensal';
                document.getElementById('data_final_recorrencia').value = '';
            }
        });
    }
    
    // Lógica para ABRIR o modal de ADICIONAR transação
    const addBtn = document.getElementById('openAddModalBtn');
    if (addBtn) {
        addBtn.addEventListener('click', function(e) {
            e.preventDefault();
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            modalLabel.textContent = 'Adicionar Transação';
            form.action = addUrl;
            form.reset(); 
            if(valorMask) valorMask.unmaskedValue = '';
            
            const hoje = new Date();
            const ano = hoje.getFullYear();
            const mes = String(hoje.getMonth() + 1).padStart(2, '0');
            const dia = String(hoje.getDate()).padStart(2, '0');
            document.getElementById('data').value = `${ano}-${mes}-${dia}`;
            
            if(recorrenciaSwitch) {
                recorrenciaSwitch.checked = false;
                recorrenciaSwitch.dispatchEvent(new Event('change'));
            }
            filtrarCategorias();
            modal.show();
        });
    }

    // Lógica para ABRIR o modal de EDITAR transação
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            modalLabel.textContent = 'Editar Transação';
            form.reset();
            const id = this.dataset.id;
            form.action = `/transacoes/editar/${id}`;
            form.querySelector('#edit-id').value = id;
            document.getElementById('tipo').value = this.dataset.tipo;
            if(valorMask) valorMask.unmaskedValue = this.dataset.valor;
            document.getElementById('descricao').value = this.dataset.descricao;
            document.getElementById('data').value = this.dataset.data;
            document.getElementById('forma_pagamento').value = this.dataset.formaPagamento;
            if (recorrenciaSwitch) {
                const recorrencia = this.dataset.recorrencia;
                recorrenciaSwitch.checked = !!recorrencia;
                document.getElementById('recorrencia').value = recorrencia || 'Mensal';
                document.getElementById('data_final_recorrencia').value = this.dataset.dataFinal;
                recorrenciaSwitch.dispatchEvent(new Event('change'));
            }
            filtrarCategorias(this.dataset.tipo);
            document.getElementById('categoria_id').value = this.dataset.categoriaId;
            modal.show();
        });
    });
    
    // Função para filtrar o dropdown de categorias
    function filtrarCategorias(tipoTransacao = null) {
        if (tipoTransacao === null) tipoTransacao = document.getElementById('tipo').value;
        const selectCategoria = document.getElementById('categoria_id');
        if(!selectCategoria) return;
        let primeiraOpcaoVisivel = null;
        selectCategoria.querySelectorAll('option').forEach(option => {
            if (!option.value) return; 
            const tipoCategoria = option.dataset.tipoCategoria;
            const deveSerVisivel = (tipoCategoria === 'Ambos' || tipoCategoria === tipoTransacao);
            option.style.display = deveSerVisivel ? '' : 'none';
            if (deveSerVisivel && !primeiraOpcaoVisivel) primeiraOpcaoVisivel = option;
        });
        if (selectCategoria.options[selectCategoria.selectedIndex] && selectCategoria.options[selectCategoria.selectedIndex].style.display === 'none') {
            selectCategoria.value = primeiraOpcaoVisivel ? primeiraOpcaoVisivel.value : '';
        }
    }
    const tipoSelect = document.getElementById('tipo');
    if(tipoSelect) { tipoSelect.addEventListener('change', () => filtrarCategorias()); }

    // Lógica para o modal de adicionar categoria rápida
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
            fetch(addCatUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ nome: nomeInput.value, tipo: tipoInput.value })
            })
            .then(response => response.json())
            .then(data => {
                nomeInput.classList.remove('is-invalid');
                if (data.success) {
                    const mainCategorySelect = document.getElementById('categoria_id');
                    const optionText = `${data.categoria.nome} (${data.categoria.tipo})`;
                    const newOption = new Option(optionText, data.categoria.id, false, true);
                    newOption.dataset.tipoCategoria = data.categoria.tipo;
                    mainCategorySelect.add(newOption);
                    mainCategorySelect.value = data.categoria.id;
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

    // Lógica do lançamento inteligente
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
                    if (data.sugestao_categoria_id) { document.getElementById('categoria_id').value = data.sugestao_categoria_id; }
                    if (data.sugestao_forma_pagamento) { document.getElementById('forma_pagamento').value = data.sugestao_forma_pagamento; }
                });
            }, 500);
        });
    }
    
    // Lógica dos botões de valor rápido
    const quickValueButtons = document.querySelectorAll('.quick-value-btn');
    if (valorMask) {
        quickValueButtons.forEach(button => {
            button.addEventListener('click', function() {
                const valueStr = this.textContent.replace(',', '.');
                valorMask.unmaskedValue = valueStr;
                valorInput.focus();
            });
        });
    }
});