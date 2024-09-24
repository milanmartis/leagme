self.addEventListener('install', (event) => {
  console.log('Service Worker installed');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activated');
});

navigator.serviceWorker.ready.then((registration) => {
  console.log('Service Worker is active and ready with scope:', registration.scope);
}).catch((error) => {
  console.error('Service Worker is not ready:', error);
});