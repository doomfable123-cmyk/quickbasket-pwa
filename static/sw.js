// QuickBasket Service Worker
// Provides offline functionality and app-like experience

const CACHE_NAME = 'quickbasket-v1.0.0';
const BASE_CACHE = [
  '/',
  '/recipes/',
  '/grocery_list/',
  '/add-recipe-url/',
  '/add-recipe-manual/',
  '/static/manifest.json'
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
  console.log('QuickBasket Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('QuickBasket Service Worker: Caching essential files');
        return cache.addAll(BASE_CACHE);
      })
      .catch(err => {
        console.error('QuickBasket Service Worker: Install failed:', err);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('QuickBasket Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('QuickBasket Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache when offline, with network-first strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-HTTP requests
  if (!request.url.startsWith('http')) {
    return;
  }

  // Handle API requests with network-first strategy (for real-time data)
  if (url.pathname.startsWith('/api/') || 
      url.pathname.includes('add-recipe') || 
      url.pathname.includes('delete-recipe') ||
      url.pathname.includes('grocery_list')) {
    
    event.respondWith(
      fetch(request)
        .then(response => {
          // If request is successful, clone and cache the response
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(request).then(cachedResponse => {
            if (cachedResponse) {
              return cachedResponse;
            }
            // If no cached response, return offline page or error
            return new Response(
              JSON.stringify({
                error: 'Offline - This feature requires internet connection',
                offline: true
              }),
              {
                status: 503,
                statusText: 'Service Unavailable',
                headers: { 'Content-Type': 'application/json' }
              }
            );
          });
        })
    );
    return;
  }

  // Handle static assets and pages with cache-first strategy
  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        return fetch(request)
          .then(response => {
            // Don't cache if not a valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            const responseClone = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(request, responseClone);
              });

            return response;
          })
          .catch(() => {
            // If both cache and network fail, return offline page
            if (request.destination === 'document') {
              return caches.match('/') || new Response(
                '<h1>QuickBasket - Offline</h1><p>Please check your internet connection and try again.</p>',
                { headers: { 'Content-Type': 'text/html' } }
              );
            }
          });
      })
  );
});

// Handle background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('QuickBasket Service Worker: Background sync triggered');
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Here you could implement offline action queuing
      // For now, just log that sync is available
      console.log('QuickBasket Service Worker: Background sync available for future offline actions')
    );
  }
});

// Handle push notifications (for future enhancement)
self.addEventListener('push', (event) => {
  console.log('QuickBasket Service Worker: Push notification received');
  // Could be used for recipe reminders or grocery list updates
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});