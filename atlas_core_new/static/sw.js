const CACHE_NAME = 'atlas-core-v1.6.0';
const STATIC_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
  '/static/images/ajani_bg.png',
  '/static/images/counsel_bg.png',
  '/static/images/icon-192.png',
  '/static/images/icon-512.png'
];

const API_CACHE_NAME = 'atlas-api-v1';
const API_CACHE_DURATION = 5 * 60 * 1000;

self.addEventListener('install', (event) => {
  console.log('[SW] Installing Atlas Core service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS.filter(url => !url.includes('icon-')));
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
          .filter((name) => name !== CACHE_NAME && name !== API_CACHE_NAME)
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
