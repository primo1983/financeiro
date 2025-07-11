document.addEventListener('DOMContentLoaded', function() {
    const themeRadios = document.querySelectorAll('input[name="theme-options"]');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const newTheme = this.value;
            // Muda o tema da página instantaneamente
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            
            // Envia a nova preferência para o backend para salvar
            fetch("/salvar-tema", { // A rota foi corrigida de /auth/salvar-tema para /salvar-tema
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ theme: newTheme })
            })
            .then(response => {
                // DEBUG: Mostra o status da resposta do servidor
                console.log("DEBUG: Resposta do servidor:", response.status, response.statusText);
                if (!response.ok) {
                    console.error("Erro na resposta do servidor.");
                }
                return response.json();
            })
            .then(data => {
                // DEBUG: Mostra os dados retornados pelo servidor
                console.log("DEBUG: Dados da resposta:", data);
                if (data.success) {
                    console.log("Tema salvo com sucesso no banco de dados!");
                } else {
                    console.error("Ocorreu um erro no servidor ao salvar o tema.");
                }
            })
            .catch(error => {
                console.error("Erro de comunicação ao salvar o tema:", error);
            });
        });
    });
});