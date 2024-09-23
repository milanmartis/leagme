// Import Firebase App and Firebase Messaging modules
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js';
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js';

// Kontrola podpory IndexedDB
function isIndexedDBAvailable() {
  return typeof indexedDB !== 'undefined';
}
// console.log("eee",vapidPublicKey);
// Funkcia na získanie povolenia na notifikácie
function requestNotificationPermission(messaging) {
  Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
      console.log('Notification permission granted.');
      // Registrácia Service Worker a získanie tokenu s použitím VAPID public key
      navigator.serviceWorker.register('/js/firebase-messaging-sw.js')
        .then((registration) => {
          return getToken(messaging, {
            vapidKey: vapidPublicKey,  // Použitie VAPID key
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

// Inicializácia Firebase a FCM
function initializeFirebase() {
  fetch('/get-firebase-config')
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
