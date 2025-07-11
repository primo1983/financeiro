document.addEventListener('DOMContentLoaded', function () {
    /**
     * Função para lidar com a submissão de formulários via AJAX nesta página específica.
     * Ela entende como usar a 'redirect_url' retornada pelo backend.
     * @param {string} formId O ID do formulário HTML a ser observado.
     */
    const handleAdminFormSubmit = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                if (ok && body.success) {
                    // CORREÇÃO APLICADA AQUI:
                    // Se o backend enviar uma URL de redirecionamento, usa-a.
                    if (body.redirect_url) {
                        window.location.href = body.redirect_url;
                    } else {
                        // Senão, apenas recarrega a página.
                        window.location.reload();
                    }
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
    handleAdminFormSubmit('addUserForm');
    handleAdminFormSubmit('editUserForm');

    // Lógica para preencher o modal de edição ao clicar no botão
    const editModalEl = document.getElementById('editUserModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        // Usando delegação de eventos para funcionar com conteúdo dinâmico se necessário
        document.body.addEventListener('click', function(event) {
            const button = event.target.closest('.edit-btn');
            if (!button) return;

            const form = document.getElementById('editUserForm');
            const id = button.dataset.id;
            
            form.action = `/admin/usuarios/editar/${id}`;
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            document.getElementById('edit-username-title').textContent = button.dataset.username;
            const usernameInput = form.querySelector('#edit_username');
            if (usernameInput) usernameInput.value = button.dataset.username;

            form.querySelector('#edit_email').value = button.dataset.email;
            form.querySelector('#edit_is_admin').checked = (button.dataset.is_admin === 'true');
            form.querySelector('#edit_password').value = ''; 
            
            editModal.show();
        });
    }
});