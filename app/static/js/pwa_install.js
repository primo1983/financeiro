// Variável para guardar o evento de instalação, agora fora do listener
let deferredPrompt;

/**
 * Verifica se o dispositivo do usuário é um telemóvel ou tablet.
 * @returns {boolean} True se for um dispositivo móvel, senão False.
 */
function isMobile() {
    const userAgentCheck = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const touchCheck = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
    return userAgentCheck && touchCheck;
}

/**
 * Mostra os botões de instalação se as condições forem satisfeitas.
 */
function showInstallPromotion() {
    // Só mostra se o convite do navegador existir E se for um dispositivo móvel
    if (deferredPrompt && isMobile()) {
        const installButtonLogin = document.getElementById('botao-instalar-pwa');
        const installMenuItem = document.getElementById('menu-instalar-pwa');
        
        if (installButtonLogin) installButtonLogin.style.display = 'block';
        if (installMenuItem) installMenuItem.style.display = 'block';
    }
}

// Ouve o evento do navegador que nos permite instalar a app
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  console.log('PWA: Convite de instalação guardado.');
  // Assim que o convite é recebido, tentamos mostrar os botões
  showInstallPromotion();
});

// Função que será chamada pelo clique dos botões
const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    
    // Esconde os botões para não serem clicados novamente
    const installButtonLogin = document.getElementById('botao-instalar-pwa');
    const installMenuItem = document.getElementById('menu-instalar-pwa');
    if (installButtonLogin) installButtonLogin.style.display = 'none';
    if (installMenuItem) installMenuItem.style.display = 'none';

    // Mostra o prompt de instalação nativo
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User response to the install prompt: ${outcome}`);
    deferredPrompt = null;
};

// Quando a página carregar, anexa a função de clique aos botões
document.addEventListener('DOMContentLoaded', () => {
    const installButtonLogin = document.getElementById('botao-instalar-pwa');
    const installMenuItem = document.getElementById('menu-instalar-pwa');

    if (installButtonLogin) installButtonLogin.addEventListener('click', handleInstallClick);
    if (installMenuItem) installMenuItem.addEventListener('click', handleInstallClick);

    // Verifica também no carregamento da página, caso o evento já tenha acontecido
    showInstallPromotion();
});


window.addEventListener('appinstalled', () => {
  deferredPrompt = null;
  console.log('PWA foi instalada com sucesso!');
});