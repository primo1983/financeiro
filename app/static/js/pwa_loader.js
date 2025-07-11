if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Pega a URL do sw.js a partir do atributo data no body
        const swUrl = document.body.dataset.swUrl; 
        
        if (swUrl) {
            // Registra o Service Worker com o escopo correto
            navigator.serviceWorker.register(swUrl, { scope: '/' })
                .then(registration => {
                    console.log('Service Worker registrado com sucesso com escopo /:', registration);
                })
                .catch(error => {
                    console.log('Falha ao registrar o Service Worker:', error);
                });
        }
    });
}