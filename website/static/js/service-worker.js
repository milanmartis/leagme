// Import Firebase SDK pre Cloud Messaging
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');

// Načítanie Firebase konfigurácie z backendu (súbor musí byť už inicializovaný na klientovi)
self.addEventListener('install', event => {
  event.waitUntil(
    fetch('/get-firebase-config')
      .then(response => response.json())
      .then(firebaseConfig => {
        // Inicializácia Firebase vo service worker
        firebase.initializeApp(firebaseConfig);

        // Inicializácia Firebase Cloud Messaging
        const messaging = firebase.messaging();

        // Spracovanie push notifikácií na pozadí
        messaging.onBackgroundMessage((payload) => {
          console.log('[Service Worker] Background message received:', payload);
          const notificationTitle = payload.notification.title;
          const notificationOptions = {
            body: payload.notification.body,
            icon: '/static/img/icon.png'  // Nastav si cestu k tvojej ikone
          };
          self.registration.showNotification(notificationTitle, notificationOptions);
        });
      })
      .catch(error => {
        console.error('Error during Firebase initialization in Service Worker:', error);
      })
  );
});

// Spracovanie push notifikácií na pozadí pre Web Push API (napr. pre desktopové prehliadače)
self.addEventListener('push', function(event) {
  const data = event.data.json();
  console.log('[Service Worker] Push notification received:', data);

  const options = {
    body: data.body,
    icon: '/static/img/icon.png'
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Ošetrenie notifikácie pri kliknutí
self.addEventListener('notificationclick', function(event) {
  console.log('[Service Worker] Notification click received.');
  event.notification.close();

  // Otvoriť alebo presmerovať na konkrétnu stránku
  event.waitUntil(
    clients.openWindow('/')
  );
});
