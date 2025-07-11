document.addEventListener('DOMContentLoaded', function () {
    // Chama a função genérica para os dois formulários desta página
    handleAjaxFormSubmit('addUserForm');
    handleAjaxFormSubmit('editUserForm');

    // Lógica para preencher o modal de edição ao clicar no botão
    const editModalEl = document.getElementById('editUserModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.body.addEventListener('click', function(event) {
            const button = event.target.closest('.edit-btn');
            // Garante que só afeta os botões da tabela de admin
            if (!button || !button.closest('#admin-user-table')) return;

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