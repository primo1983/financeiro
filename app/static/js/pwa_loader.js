if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const swUrl = '/sw.js';
        navigator.serviceWorker.register(swUrl, { scope: '/' })
            .then(registration => {
                // Removido o console.log para um código mais limpo
            })
            .catch(error => {
                console.log('Falha ao registrar o Service Worker:', error);
            });
    });
}