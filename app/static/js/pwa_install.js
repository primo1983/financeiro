if (!window.pwaInstallerLoaded) {
    window.pwaInstallerLoaded = true;

    let deferredPrompt;

    function isMobile() {
        const userAgentCheck = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const touchCheck = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        return userAgentCheck && touchCheck;
    }

    function showInstallPromotion() {
        if (deferredPrompt && isMobile()) {
            const installButtonLogin = document.getElementById('botao-instalar-pwa');
            const installMenuItem = document.getElementById('menu-instalar-pwa');
            if (installButtonLogin) installButtonLogin.style.display = 'block';
            if (installMenuItem) installMenuItem.style.display = 'block';
        }
    }

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      sessionStorage.setItem('pwa-installable', 'true');
      showInstallPromotion();
    });

    const handleInstallClick = async () => {
        if (!deferredPrompt) return;
        
        const installButtonLogin = document.getElementById('botao-instalar-pwa');
        const installMenuItem = document.getElementById('menu-instalar-pwa');
        if (installButtonLogin) installButtonLogin.style.display = 'none';
        if (installMenuItem) installMenuItem.style.display = 'none';

        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        deferredPrompt = null;
    };

    document.body.addEventListener('click', function(event) {
        if (event.target.id === 'botao-instalar-pwa' || event.target.closest('#menu-instalar-pwa')) {
            handleInstallClick();
        }
    });

    window.addEventListener('appinstalled', () => {
      deferredPrompt = null;
      sessionStorage.removeItem('pwa-installable');
    });

    document.addEventListener('DOMContentLoaded', showInstallPromotion);
}