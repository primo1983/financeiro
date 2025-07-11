// app/static/js/pwa_loader.js
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        const swUrl = document.body.dataset.swUrl; // Pega a URL do atributo do body
        if (swUrl) {
            navigator.serviceWorker.register(swUrl)
                .then(registration => {
                    console.log('Service Worker registrado com sucesso:', registration);
                })
                .catch(error => {
                    console.log('Falha ao registrar o Service Worker:', error);
                });
        }
    });
}