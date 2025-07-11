document.addEventListener('DOMContentLoaded', function () {
    // --- LÓGICA DE PRIVACIDADE DOS CARDS ---
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

    /**
     * Verifica se o dispositivo do usuário é um telemóvel ou tablet.
     * @returns {boolean} True se for um dispositivo móvel, senão False.
     */
    function isMobile() {
        const userAgentCheck = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const touchCheck = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        return userAgentCheck && touchCheck;
    }

    const pwaPromptShown = sessionStorage.getItem('pwaPromptShown');
    const isRunningInBrowser = !window.matchMedia('(display-mode: standalone)').matches;
    
    // Só mostra a dica se:
    // 1. Estiver no navegador
    // 2. A dica ainda não foi mostrada nesta sessão
    // 3. FOR UM DISPOSITIVO MÓVEL
    if (isRunningInBrowser && !pwaPromptShown && isMobile()) {
        const pwaPromptEl = document.getElementById('pwa-prompt');
        if (pwaPromptEl) {
            pwaPromptEl.classList.remove('d-none');
            sessionStorage.setItem('pwaPromptShown', 'true');
        }
    }
});