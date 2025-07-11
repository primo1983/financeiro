document.addEventListener('DOMContentLoaded', function () {
    let deferredPrompt;
    const installButtonLogin = document.getElementById('botao-instalar-pwa');
    const installMenuItem = document.getElementById('menu-instalar-pwa');

    function isMobile() {
        const userAgentCheck = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const touchCheck = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        return userAgentCheck && touchCheck;
    }

    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;

        // --- MUDANÇA APLICADA AQUI ---
        // Guarda na memória da sessão que a app pode ser instalada
        sessionStorage.setItem('pwa-installable', 'true');
        
        if (isMobile()) {
            if (installButtonLogin) installButtonLogin.style.display = 'block';
            if (installMenuItem) installMenuItem.style.display = 'block';
        }
    });

    const handleInstallClick = async () => {
        if (!deferredPrompt) return;
        
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        deferredPrompt = null;

        if (installButtonLogin) installButtonLogin.style.display = 'none';
        if (installMenuItem) installMenuItem.style.display = 'none';
    };

    if (installButtonLogin) installButtonLogin.addEventListener('click', handleInstallClick);
    if (installMenuItem) installMenuItem.addEventListener('click', handleInstallClick);

    window.addEventListener('appinstalled', () => {
        deferredPrompt = null;
        // Se a app for instalada, removemos a "pista"
        sessionStorage.removeItem('pwa-installable');
        if (installButtonLogin) installButtonLogin.style.display = 'none';
        if (installMenuItem) installMenuItem.style.display = 'none';
        console.log('PWA foi instalada');
    });
});