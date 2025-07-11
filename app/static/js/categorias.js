document.addEventListener('DOMContentLoaded', function () {
    // Chama a função genérica para os dois formulários desta página
    handleAjaxFormSubmit('addCategoryForm');
    handleAjaxFormSubmit('editCategoryForm');

    // Lógica para preencher o modal de edição
    const editModalEl = document.getElementById('editCategoryModal');
    if (editModalEl) {
        const editModal = new bootstrap.Modal(editModalEl);
        document.body.addEventListener('click', function(event) {
            const button = event.target.closest('.edit-btn');
             // Garante que só afeta os botões da tabela de categorias
            if (!button || !button.closest('#category-table')) return;

            const id = button.dataset.id;
            const form = document.getElementById('editCategoryForm');
            form.action = `/categorias/editar/${id}`;
            
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            form.querySelector('#edit-id').value = id;
            form.querySelector('#edit-nome').value = button.dataset.nome;
            form.querySelector('#edit-tipo').value = button.dataset.tipo;
            editModal.show();
        });
    }
});