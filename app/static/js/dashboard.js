document.addEventListener('DOMContentLoaded', function () {
    // --- LÓGICA DE PRIVACIDADE DOS CARDS (JÁ EXISTENTE E CORRETA) ---
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

    // --- LÓGICA CORRIGIDA PARA SUGESTÃO DE PWA ---
    const pwaPromptShown = sessionStorage.getItem('pwaPromptShown');
    const isRunningInBrowser = !window.matchMedia('(display-mode: standalone)').matches;
    
    // Lê a "pista" que o pwa_install.js pode ter deixado
    const isInstallable = sessionStorage.getItem('pwa-installable');
    
    // Só mostra a dica se:
    // 1. Estiver no navegador
    // 2. A dica ainda não foi mostrada nesta sessão
    // 3. A app NÃO for "instalável" (o que implica que ela JÁ foi instalada)
    if (isRunningInBrowser && !pwaPromptShown && !isInstallable) {
        const pwaPromptEl = document.getElementById('pwa-prompt');
        if (pwaPromptEl) {
            pwaPromptEl.classList.remove('d-none');
            sessionStorage.setItem('pwaPromptShown', 'true');
        }
    }
});