document.addEventListener('DOMContentLoaded', function () {
    // Lógica para preencher o modal de edição ao clicar no botão
    const editModalEl = document.getElementById('editCategoryModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function () {
                const id = this.dataset.id;
                const form = document.getElementById('editCategoryForm');
                form.action = `/categorias/editar/${id}`;
                
                // Limpa erros de validação antigos antes de preencher
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                form.querySelector('#edit-id').value = id;
                form.querySelector('#edit-nome').value = this.dataset.nome;
                form.querySelector('#edit-tipo').value = this.dataset.tipo;
                editModal.show();
            });
        });
    }

    // Função genérica para lidar com o envio de formulários via AJAX
    const handleAjaxFormSubmit = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');
            const csrfToken = form.querySelector('[name="csrf_token"]').value;

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json().then(data => ({ ok: response.ok, body: data })))
            .then(({ ok, body }) => {
                // Remove todas as classes de erro antes de processar a resposta
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                if (ok && body.success) {
                    // Recarrega a página em caso de sucesso
                    window.location.reload();
                } else {
                    // Mostra os erros nos campos correspondentes
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
    };
    
    // Aplica a função AJAX para os dois formulários da página
    handleAjaxFormSubmit('addCategoryForm');
    handleAjaxFormSubmit('editCategoryForm');
});