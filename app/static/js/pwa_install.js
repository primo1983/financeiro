// Este script lida com a lógica de instalação do PWA
let deferredPrompt;
const installButton = document.getElementById('botao-instalar-pwa');

window.addEventListener('beforeinstallprompt', (e) => {
  // Previne que o mini-infobar do Chrome apareça
  e.preventDefault();
  // Guarda o evento para que ele possa ser disparado mais tarde.
  deferredPrompt = e;
  // Mostra o nosso botão de instalação personalizado.
  if (installButton) {
    installButton.style.display = 'block';
  }
});

if (installButton) {
  installButton.addEventListener('click', async () => {
    // Esconde o nosso botão, pois o prompt será mostrado.
    installButton.style.display = 'none';
    if (!deferredPrompt) {
      return;
    }
    // Mostra o prompt de instalação do navegador.
    deferredPrompt.prompt();
    // Espera o usuário responder ao prompt.
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`User response to the install prompt: ${outcome}`);
    // Não precisamos mais do prompt, limpamos a variável.
    deferredPrompt = null;
  });
}

window.addEventListener('appinstalled', () => {
  // Esconde o botão de instalação se a app for instalada.
  if (installButton) {
    installButton.style.display = 'none';
  }
  deferredPrompt = null;
  console.log('PWA foi instalada');
});