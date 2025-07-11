if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Agora aponta diretamente para a nossa nova rota
        const swUrl = '/sw.js'; 
        
        navigator.serviceWorker.register(swUrl, { scope: '/' })
            .then(registration => {
                console.log('Service Worker registrado com sucesso com escopo /:', registration);
            })
            .catch(error => {
                console.log('Falha ao registrar o Service Worker:', error);
            });
    });
}