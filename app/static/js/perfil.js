document.addEventListener('DOMContentLoaded', function() {
    const themeRadios = document.querySelectorAll('.btn-check[name="theme-options"]');
    // Pega o token CSRF da tag meta no HTML
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    themeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const newTheme = this.value;
            // Muda o tema da página instantaneamente
            document.documentElement.setAttribute('data-bs-theme', newTheme);
            
            // Envia a nova preferência para o backend para salvar
            // Usamos um caminho estático porque url_for() não funciona em arquivos .js
            fetch("/auth/salvar-tema", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ theme: newTheme })
            });
        });
    });
});