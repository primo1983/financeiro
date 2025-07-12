/**
 * Função genérica para lidar com a submissão de formulários via AJAX.
 * @param {string} formId O ID do formulário HTML a ser observado.
 */
function handleAjaxFormSubmit(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const actionUrl = form.getAttribute('action');
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) submitButton.disabled = true;

        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json().then(data => ({ ok: response.ok, status: response.status, body: data })))
        .then(({ ok, body }) => {
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            if (ok && body.success) {
                // --- LÓGICA ATUALIZADA AQUI ---
                // Se o backend enviar uma URL, redireciona para ela.
                if (body.redirect_url) {
                    window.location.href = body.redirect_url;
                } else {
                    // Senão, apenas recarrega a página.
                    window.location.reload();
                }
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
        }).finally(() => {
            if (submitButton) submitButton.disabled = false;
        });
    });
}