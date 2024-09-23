// Import Firebase App and Firebase Messaging modules
import { initializeApp } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js';
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js';

// Kontrola podpory IndexedDB
function isIndexedDBAvailable() {
  return typeof indexedDB !== 'undefined';
}
// alert(vapidPublicKey);
// console.log("eee",vapidPublicKey);
// Funkcia na získanie povolenia na notifikácie
function requestNotificationPermission(messaging) {
    Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
            console.log('Notification permission granted.');
            // Get registration token for FCM
            getToken(messaging, { vapidKey: vapidPublicKey })
            .then((currentToken) => {
                if (currentToken) {
                    console.log('FCM token:', currentToken);
                    // Send the token to your server or save it locally
                } else {
                    console.log('No registration token available. Request permission to generate one.');
                }
            })
            .catch((err) => {
                console.error('An error occurred while retrieving token. ', err);
            });
        } else {
            console.log('Unable to get permission to notify.');
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
