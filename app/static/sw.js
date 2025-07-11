const CACHE_NAME = 'minhas-financas-cache-v1';
// Lista de arquivos para guardar em cache na instalação
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/css/bootstrap.min.css',
  '/static/js/filtros.js',
  '/static/js/modal_transacao.js'
];

// Evento de instalação: abre o cache e adiciona os arquivos
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Evento de fetch: responde com o cache se disponível, senão vai à rede
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Se encontrar no cache, retorna o cache
        if (response) {
          return response;
        }
        // Senão, faz o pedido na rede
        return fetch(event.request);
      }
    )
  );
});