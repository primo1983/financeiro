document.addEventListener('DOMContentLoaded', function () {
    // --- LÓGICA DE PRIVACIDADE DOS CARDS (JÁ EXISTENTE) ---
    const toggleButtons = document.querySelectorAll('.toggle-saldo-btn');
    if (toggleButtons.length > 0) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const url = '/toggle-card-visibility';

        toggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const cardName = this.dataset.cardName;
                const cardValue = this.dataset.cardValue;
                const valorElement = document.getElementById(`${cardName}-valor`);
                const iconElement = document.getElementById(`${cardName}-icon`);
                if (!valorElement || !iconElement) return;

                const isCurrentlyVisible = !iconElement.classList.contains('bi-eye');
                if (isCurrentlyVisible) {
                    valorElement.textContent = 'R$ ••••••';
                    iconElement.classList.replace('bi-eye-slash', 'bi-eye');
                } else {
                    valorElement.textContent = cardValue;
                    iconElement.classList.replace('bi-eye', 'bi-eye-slash');
                }

                fetch(url, { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                    body: JSON.stringify({ card: cardName })
                }).catch(error => console.error('Falha ao salvar preferência:', error));
            });
        });
    }

    // --- NOVA LÓGICA PARA SUGESTÃO DE PWA ---
    // Verifica se a app NÃO está a rodar em modo standalone (ou seja, está numa aba do navegador)
    const isInBrowser = !window.matchMedia('(display-mode: standalone)').matches;
    
    // Verifica se a app já foi "instalada" alguma vez (só para ter mais certeza)
    // E se a mensagem já foi mostrada nesta sessão
    if (isInBrowser && navigator.standalone !== undefined && !sessionStorage.getItem('pwaPromptShown')) {
        const pwaPrompt = document.getElementById('pwa-prompt');
        if (pwaPrompt) {
            pwaPrompt.classList.remove('d-none');
            // Marca que a mensagem foi mostrada para não a mostrar novamente se o usuário recarregar a página
            sessionStorage.setItem('pwaPromptShown', 'true');
        }
    }
});