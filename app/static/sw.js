// A versão do cache é incrementada para forçar o navegador a atualizar os arquivos
const CACHE_NAME = 'minhas-financas-cache-v3'; 
const urlsToCache = [
  '/', // A página principal para garantir que a app sempre abra offline
  '/static/css/style.css',
  '/static/css/bootstrap.min.css',
  '/static/css/bootstrap-icons.min.css'
];

// Evento de Instalação: guarda os arquivos base em cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto e arquivos base adicionados');
        return cache.addAll(urlsToCache);
      })
  );
});

// Evento de Ativação: limpa caches antigos para manter tudo limpo
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            console.log('A limpar cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Evento de Fetch: estratégia "Network Falling Back to Cache" melhorada
self.addEventListener('fetch', event => {
  // Ignora pedidos que não são GET (ex: POST para formulários)
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    // 1. Tenta buscar na rede primeiro
    fetch(event.request)
      .then(networkResponse => {
        // Se o pedido for bem-sucedido, guarda uma cópia no cache para uso offline futuro
        
        // Verifica se a resposta é válida antes de guardar em cache
        // Respostas do tipo 'basic' são do nosso próprio domínio.
        // Respostas opacas (de CDNs) ou de erro não devem ser guardadas.
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
        }

        return networkResponse;
      })
      .catch(() => {
        // 2. Se a rede falhar (ex: offline), tenta responder com o que está no cache
        return caches.match(event.request);
      })
  );
});