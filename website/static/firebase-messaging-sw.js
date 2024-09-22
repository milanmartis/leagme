// Importovanie Firebase SDK pre Service Worker
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');

// Načítanie Firebase konfigurácie z backendu počas inštalácie Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    fetch('/get-firebase-config')
      .then(response => response.json())
      .then(firebaseConfig => {
        // Inicializácia Firebase vo Service Worker
        firebase.initializeApp(firebaseConfig);
      })
  );
});

// Po inštalácii je potrebné spracovať background messages
self.addEventListener('activate', event => {
  event.waitUntil(
    self.clients.claim()  // Akonáhle je nainštalovaný, tento Service Worker bude aktívny okamžite
  );
});

// Inicializácia Firebase Messaging po aktivácii Service Worker
const messaging = firebase.messaging();

// Spracovanie správ na pozadí (background messages)
messaging.onBackgroundMessage(function(payload) {
  console.log('Prijatá správa na pozadí:', payload);
  
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/firebase-logo.png'  // Upravte si cestu k ikone, ak potrebujete
  };

  // Zobrazenie notifikácie
  self.registration.showNotification(notificationTitle, notificationOptions);
});
