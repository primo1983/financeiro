document.addEventListener('DOMContentLoaded', function () {
    // A função AJAX agora é chamada a partir do nosso script central
    handleAjaxFormSubmit('addUserForm');
    handleAjaxFormSubmit('editUserForm');

    // A lógica para preencher o modal de edição continua aqui, pois é específica desta página.
    const editModalEl = document.getElementById('editUserModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function() {
                const form = document.getElementById('editUserForm');
                const id = this.dataset.id;
                
                form.action = `/admin/usuarios/editar/${id}`;
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                document.getElementById('edit-username-title').textContent = this.dataset.username;
                // O campo username no form de edição é apenas de leitura, então não precisa de um 'value'
                document.getElementById('edit_email').value = this.dataset.email;
                document.getElementById('edit_is_admin').checked = (this.dataset.is_admin === 'true');
                document.getElementById('edit_password').value = ''; 
                
                editModal.show();
            });
        });
    }
});