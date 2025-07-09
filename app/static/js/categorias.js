document.addEventListener('DOMContentLoaded', function () {
    // A função AJAX agora é chamada a partir do nosso script central
    handleAjaxFormSubmit('addCategoryForm');
    handleAjaxFormSubmit('editCategoryForm');

    // A lógica para preencher o modal de edição continua aqui.
    const editModalEl = document.getElementById('editCategoryModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.querySelectorAll('.edit-btn').forEach(button => {
            button.addEventListener('click', function () {
                const id = this.dataset.id;
                const form = document.getElementById('editCategoryForm');
                form.action = `/categorias/editar/${id}`;
                
                form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
                
                form.querySelector('#edit-id').value = id;
                form.querySelector('#edit-nome').value = this.dataset.nome;
                form.querySelector('#edit-tipo').value = this.dataset.tipo;
                editModal.show();
            });
        });
    }
});