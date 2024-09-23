importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Inicializácia Firebase v Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    fetch('/get-firebase-config', {
      headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/json',
      }
    })
      .then(response => response.json())
      .then(firebaseConfig => {
        firebase.initializeApp(firebaseConfig);

        const messaging = firebase.messaging();
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