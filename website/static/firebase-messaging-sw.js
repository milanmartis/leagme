// Importovanie Firebase SDK pre Service Worker
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');

// Načítanie Firebase konfigurácie z backendu
self.addEventListener('install', event => {
  event.waitUntil(
    fetch('/get-firebase-config') // Endpoint, kde načítaš konfiguráciu
      .then(response => response.json())
      .then(firebaseConfig => {
        // Inicializácia Firebase vo Service Worker
        firebase.initializeApp(firebaseConfig);

        // Inicializácia Firebase Cloud Messaging
        const messaging = firebase.messaging();

        // Spracovanie notifikácií, ktoré prichádzajú, keď je aplikácia na pozadí
        messaging.onBackgroundMessage(function(payload) {
          console.log('Prijatá správa na pozadí:', payload);

          const notificationTitle = payload.notification.title;
          const notificationOptions = {
            body: payload.notification.body,
            icon: '/firebase-logo.png' // Tu môžeš nastaviť ikonu notifikácie
          };

          // Zobrazenie notifikácie
          self.registration.showNotification(notificationTitle, notificationOptions);
        });
      })
  );
});
