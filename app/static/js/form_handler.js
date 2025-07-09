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

        // Mostra um spinner ou desativa o botão de submit (opcional, para melhor UX)
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
        .then(({ ok, status, body }) => {
            // Limpa erros de validação antigos
            form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
            
            if (ok && body.success) {
                // Recarrega a página em caso de sucesso
                window.location.reload();
            } else {
                // Mostra os erros de validação nos campos correspondentes
                for (const fieldName in body.errors) {
                    const field = form.querySelector(`[name="${fieldName}"]`);
                    const feedbackDiv = field ? field.nextElementSibling : null;

                    if (field) { 
                        field.classList.add('is-invalid');
                        // Se houver uma div para feedback, insere o erro (opcional)
                        if (feedbackDiv && feedbackDiv.classList.contains('invalid-feedback')) {
                            feedbackDiv.textContent = body.errors[fieldName][0];
                        }
                    }
                }
            }
        }).catch(error => {
            console.error('Erro de Fetch:', error);
            alert('Ocorreu um erro de comunicação com o servidor.');
        }).finally(() => {
            // Reativa o botão de submit no final da operação
            if (submitButton) submitButton.disabled = false;
        });
    });
}