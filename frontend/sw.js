/**
 * 1CRYPTEN SNIPER V100 - PWA SERVICE WORKER
 * Estratégia: Stale-While-Revalidate (Main) + Cache-First (Assets)
 * Foco: Carregamento instantâneo e bypass de API
 */

const CACHE_NAME = '1crypten-sniper-v100.1';
const STATIC_ASSETS = [
    '/',
    '/cockpit.html',
    '/logo10D.png',
    '/favicon.ico',
    '/manifest.json'
];

// Instalação: Cacheia arquivos críticos
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching critical assets');
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Ativação: Limpa caches antigos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
            );
        })
    );
    console.log('[SW] V100 Activated and ready ✅');
    return self.clients.claim();
});

// Interceptor de Fetch
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // 1. BYPASS para APIs, Firebase e WebSockets
    if (url.pathname.startsWith('/api/') || 
        url.hostname.includes('firebaseio.com') || 
        url.hostname.includes('bybit') ||
        event.request.method !== 'GET') {
        return; // Network Only
    }

    // 2. Cache-First para Fontes e Ícones (CDNs)
    if (url.hostname.includes('gstatic.com') || 
        url.hostname.includes('googleapis.com') || 
        url.hostname.includes('material-icons')) {
        event.respondWith(
            caches.match(event.request).then((cached) => {
                return cached || fetch(event.request).then((response) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                });
            })
        );
        return;
    }

    // 3. Stale-While-Revalidate para o Cockpit e Manifest
    event.respondWith(
        caches.match(event.request).then((cached) => {
            const networkFetch = fetch(event.request).then((response) => {
                return caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
            return cached || networkFetch;
        })
    );
});

// Listener para mensagens (Update Protocol)
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
