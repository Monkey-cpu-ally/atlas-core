const SW_URL = new URL(self.location.href);
const SW_MODE = SW_URL.searchParams.get('mode') || 'prod';
const SW_VERSION = SW_URL.searchParams.get('v') || '1.6.0';
const DEV_MODE = SW_MODE === 'dev';

const CACHE_NAME = `atlas-core-${SW_MODE}-${SW_VERSION}`;
const STATIC_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/images/ajani_bg.png',
  '/static/images/counsel_bg.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png'
];

const API_CACHE_NAME = `atlas-api-${SW_MODE}-${SW_VERSION}`;
const API_CACHE_DURATION = 5 * 60 * 1000;

function isAtlasCacheName(name) {
  return name.startsWith('atlas-core-') || name.startsWith('atlas-api-');
}

function isStyleOrScriptRequest(request, url) {
  const destination = request.destination || '';
  return destination === 'style' ||
    destination === 'script' ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.mjs');
}

self.addEventListener('install', (event) => {
  console.log('[SW] Installing Atlas Core service worker...');
  if (DEV_MODE) {
    event.waitUntil(self.skipWaiting());
    return;
  }

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        const urlsToCache = STATIC_ASSETS.filter((url) => !url.includes('icon-'));
        return Promise.all(
          urlsToCache.map((assetUrl) =>
            cache.add(assetUrl).catch((error) => {
              console.log('[SW] Skipping precache asset:', assetUrl, error?.message || error);
            })
          )
        );
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Atlas Core service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => isAtlasCacheName(name) && name !== CACHE_NAME && name !== API_CACHE_NAME)
          .map((name) => {
            console.log('[SW] Removing old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  if (event.request.method !== 'GET') {
    return;
  }

  if (url.origin !== self.location.origin) {
    return;
  }

  if (DEV_MODE) {
    event.respondWith(devNetworkOnly(event.request));
    return;
  }

  if (isStyleOrScriptRequest(event.request, url)) {
    event.respondWith(networkOnly(event.request));
    return;
  }

  if (url.pathname.startsWith('/chat') || 
      url.pathname.startsWith('/progress') ||
      url.pathname.startsWith('/projects') ||
      url.pathname.startsWith('/knowledge-packs') ||
      url.pathname.startsWith('/conversations') ||
      url.pathname.startsWith('/ideas') ||
      url.pathname.startsWith('/streaks') ||
      url.pathname.startsWith('/insights') ||
      url.pathname.startsWith('/build-sessions') ||
      url.pathname.startsWith('/morning-briefing') ||
      url.pathname.startsWith('/counsel') ||
      url.pathname.startsWith('/generate') ||
      url.pathname.startsWith('/project-nudges') ||
      url.pathname.startsWith('/focus-mode') ||
      url.pathname.startsWith('/push') ||
      url.pathname.startsWith('/widget')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  // Always fetch HTML fresh to get latest fixes
  if (url.pathname === '/' || url.pathname.endsWith('.html')) {
    event.respondWith(networkFirst(event.request));
    return;
  }

  if (url.pathname.startsWith('/static/') || 
      url.pathname.startsWith('/css/') ||
      url.pathname.startsWith('/specs') ||
      url.pathname.startsWith('/forge/templates') ||
      url.pathname.startsWith('/lego-lessons')) {
    event.respondWith(staleWhileRevalidate(event.request));
    return;
  }

  event.respondWith(networkFirst(event.request));
});

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    return new Response(JSON.stringify({
      error: 'offline',
      message: 'You are offline. This feature requires an internet connection.'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  
  const fetchPromise = fetch(request).then((response) => {
    if (response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  }).catch(() => cached);

  return cached || fetchPromise;
}

async function networkOnly(request) {
  return fetch(request, { cache: 'no-store' });
}

async function devNetworkOnly(request) {
  try {
    return await fetch(request, { cache: 'no-store' });
  } catch (error) {
    return new Response(JSON.stringify({
      error: 'offline',
      message: 'Dev mode bypasses cache; network is currently unavailable.'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(event.data.urls);
      })
    );
  }
});

self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body || 'New message from Atlas Core',
    icon: '/static/images/icon-192.png',
    badge: '/static/images/icon-72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/',
      persona: data.persona || 'trinity'
    },
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' }
    ],
    tag: data.tag || 'atlas-notification',
    renotify: true
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'Atlas Core', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'dismiss') return;
  
  const url = event.notification.data?.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url);
            return client.focus();
          }
        }
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});
