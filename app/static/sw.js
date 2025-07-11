// Versão minimalista do Service Worker para uma aplicação online-only.
// Ele permite que a aplicação seja instalável (PWA), mas não guarda nada em cache.

const CACHE_NAME = 'minhas-financas-online-only-v1';

// O evento 'install' é disparado quando o SW é instalado.
// Deixamos vazio pois não queremos guardar nada em cache.
self.addEventListener('install', (event) => {
  console.log('Service Worker a instalar (modo online-only).');
  // Força o novo service worker a ativar imediatamente.
  self.skipWaiting();
});

// O evento 'activate' é disparado quando o SW é ativado.
// Usamos para limpar quaisquer caches de versões antigas.
self.addEventListener('activate', (event) => {
    console.log('Service Worker ativado (modo online-only).');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    // Apaga todos os caches que não são o atual.
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    // Garante que o novo service worker assuma o controlo imediatamente.
    return self.clients.claim();
});

// Propositadamente, NÃO adicionamos um 'listener' para o evento 'fetch'.
// Sem um 'fetch' listener, o Service Worker não interceta os pedidos de rede.
// O navegador irá simplesmente fazer os pedidos normalmente, como num site tradicional.