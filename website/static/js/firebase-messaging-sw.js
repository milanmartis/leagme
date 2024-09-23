importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');

// Načítanie Firebase konfigurácie z backendu
self.addEventListener('install', event => {
  event.waitUntil(
    fetch('/get-firebase-config')
      .then(response => response.json())
      .then(firebaseConfig => {
        // Inicializácia Firebase vo Service Worker
        firebase.initializeApp(firebaseConfig);

        // Inicializácia Firebase Cloud Messaging
        const messaging = firebase.messaging();

        // Nastavenie spracovania správ na pozadí
        messaging.onBackgroundMessage(function(payload) {
          console.log('Prijatá správa na pozadí:', payload);
          const notificationTitle = payload.notification.title;
          const notificationOptions = {
            body: payload.notification.body,
            icon: '/firebase-logo.png'
          };
          self.registration.showNotification(notificationTitle, notificationOptions);
        });
      })
      .catch(error => {
        console.error('Chyba pri načítaní Firebase konfigurácie:', error);
      })
  );
});
