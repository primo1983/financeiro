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

    // Esta função verifica se já mostramos a dica nesta sessão do navegador
    const pwaPromptShown = sessionStorage.getItem('pwaPromptShown');

    // Esta função verifica se estamos a correr num navegador (e não na app instalada)
    const isRunningInBrowser = !window.matchMedia('(display-mode: standalone)').matches;
    
    // Se estivermos no navegador E a dica ainda não foi mostrada nesta sessão...
    if (isRunningInBrowser && !pwaPromptShown) {
        const pwaPromptEl = document.getElementById('pwa-prompt');
        if (pwaPromptEl) {
            // Mostra a dica
            pwaPromptEl.classList.remove('d-none');
            // E guarda na memória da sessão que já a mostrámos, para não ser irritante.
            sessionStorage.setItem('pwaPromptShown', 'true');
        }
    }
});