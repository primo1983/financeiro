document.addEventListener('DOMContentLoaded', function () {
    // Função genérica para lidar com o envio de formulários via AJAX
    const handleAjaxFormSubmit = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');
            // O token CSRF é pego da tag meta na página principal
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
    handleAjaxFormSubmit('addUserForm');
    handleAjaxFormSubmit('editUserForm');

    // Lógica para preencher o modal de edição ao clicar no botão
    const editModalEl = document.getElementById('editUserModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function() {
                const form = document.getElementById('editUserForm');
                const id = this.dataset.id;
                
                form.action = `/admin/usuarios/editar/${id}`;
                
                // Limpa erros de validação antigos antes de preencher
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                document.getElementById('edit-username-title').textContent = this.dataset.username;
                document.getElementById('edit_username').value = this.dataset.username;
                document.getElementById('edit_email').value = this.dataset.email;
                document.getElementById('edit_is_admin').checked = (this.dataset.is_admin === 'true');
                document.getElementById('edit_password').value = ''; // Limpa o campo de senha
                
                editModal.show();
            });
        });
    }
});