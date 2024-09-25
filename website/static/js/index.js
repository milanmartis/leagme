import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js';
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js';

// Kontrola podpory IndexedDB
function isIndexedDBAvailable() {
  return typeof indexedDB !== 'undefined';
}

// Funkcia na získanie povolenia na notifikácie
function requestNotificationPermission(messaging) {
  Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
      console.log('Notification permission granted.');
      
      // Registrácia Service Worker a získanie tokenu s použitím VAPID public key
      navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js')
        .then((registration) => {
          return getToken(messaging, {
            vapidKey: urlBase64ToUint8Array(vapidPublicKey),  // Použitie VAPID key
            serviceWorkerRegistration: registration
          });
        })
        .then((currentToken) => {
          if (currentToken) {
            console.log('FCM token:', currentToken);
            // Odošlite tento token na backend, aby ste ho mohli uložiť
          } else {
            console.log('Nebolo možné získať FCM token.');
          }
        })
        .catch((err) => {
          console.error('Chyba pri získavaní tokenu:', err);
        });
    } else {
      console.log('Notifications permission denied');
    }
  });
}

const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Inicializácia Firebase a FCM
function initializeFirebase() {
  fetch('/get-firebase-config', {
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    }
  })
    .then(response => response.json())
    .then(firebaseConfig => {
      // Inicializácia Firebase s dynamicky načítanou konfiguráciou
      const app = initializeApp(firebaseConfig);

      // Inicializácia Firebase Cloud Messaging
      const messaging = getMessaging(app);

      // Získanie povolenia na zobrazenie notifikácií
      if (isIndexedDBAvailable()) {
        console.log("IndexedDB is available, initializing Firebase Messaging...");
        requestNotificationPermission(messaging); // Zavolanie funkcie na získanie povolenia
      } else {
        console.log("This browser doesn't support IndexedDB, FCM will not work.");
      }

      // Spracovanie správ, keď je stránka aktívna (popredí)
      onMessage(messaging, (payload) => {
        console.log('Správa prijatá:', payload);
        const notificationTitle = payload.notification.title;
        const notificationOptions = {
          body: payload.notification.body,
          icon: '/firebase-logo.png'  // Upravte cestu k vašej ikone, ak chcete
        };
        new Notification(notificationTitle, notificationOptions);
      });
    })
    .catch((error) => {
      console.error('Chyba pri načítaní Firebase konfigurácie:', error);
    });
}

// Inicializujte Firebase pri načítaní stránky
document.addEventListener('DOMContentLoaded', initializeFirebase);


navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js')
.then((registration) => {
  console.log('Service Worker successfully registered with scope:', registration.scope);
  return getToken(messaging, {
    vapidKey: vapidPublicKey,
    serviceWorkerRegistration: registration
  });
})
.then((currentToken) => {
  if (currentToken) {
    console.log('FCM token:', currentToken);
    // Odošli token na backend, aby sa uložil
  } else {
    console.log('Nebolo možné získať FCM token.');
  }
})
.catch((err) => {
  console.error('Service Worker registration failed or token retrieval error:', err);
});


// Konverzia VAPID kľúča na Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }

    return outputArray;
}
