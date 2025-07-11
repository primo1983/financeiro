document.addEventListener('DOMContentLoaded', function () {
    let deferredPrompt;
    const installButtonLogin = document.getElementById('botao-instalar-pwa');
    const installMenuItem = document.getElementById('menu-instalar-pwa');

    /**
     * Verifica de forma mais robusta se o dispositivo é um telemóvel ou tablet.
     * @returns {boolean} True se for um dispositivo móvel, senão False.
     */
    function isMobile() {
        // Verifica se o User Agent contém palavras-chave de dispositivos móveis
        const userAgentCheck = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        // Verifica se o dispositivo tem capacidade de toque.
        // A segunda condição é para compatibilidade com navegadores mais antigos.
        const touchCheck = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

        return userAgentCheck && touchCheck;
    }

    window.addEventListener('beforeinstallprompt', (e) => {
        // Previne o comportamento padrão do navegador
        e.preventDefault();
        // Guarda o evento para uso posterior
        deferredPrompt = e;

        // Só mostra os botões se a nossa verificação mais inteligente retornar 'true'.
        if (isMobile()) {
            if (installButtonLogin) {
                installButtonLogin.style.display = 'block';
            }
            if (installMenuItem) {
                installMenuItem.style.display = 'block';
            }
        }
    });

    const handleInstallClick = async () => {
        if (!deferredPrompt) {
            return;
        }
        // Mostra o prompt de instalação do navegador.
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        // Limpa o prompt, pois ele só pode ser usado uma vez.
        deferredPrompt = null;

        // Esconde os botões após a tentativa
        if (installButtonLogin) installButtonLogin.style.display = 'none';
        if (installMenuItem) installMenuItem.style.display = 'none';
    };

    if (installButtonLogin) {
        installButtonLogin.addEventListener('click', handleInstallClick);
    }
    if (installMenuItem) {
        installMenuItem.addEventListener('click', handleInstallClick);
    }

    window.addEventListener('appinstalled', () => {
        deferredPrompt = null;
        if (installButtonLogin) installButtonLogin.style.display = 'none';
        if (installMenuItem) installMenuItem.style.display = 'none';
        console.log('PWA foi instalada');
    });
});