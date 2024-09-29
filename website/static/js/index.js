import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";

const publicVapidKey = vapidPublicKey;  // Nahraď vlastným VAPID kľúčom

// Funkcia pre načítanie Firebase konfigurácie z backendu
async function fetchFirebaseConfig() {
    try {
        const response = await fetch('/get-firebase-config');  // Načítanie Firebase konfigurácie zo servera
        if (!response.ok) {
            throw new Error('Failed to fetch Firebase config.');
        }
        const firebaseConfig = await response.json();
        return firebaseConfig;
    } catch (error) {
        console.error('Error fetching Firebase config:', error);
    }
}

// Inicializácia Firebase a registrácia Service Workera
async function initializeFirebase() {
    const firebaseConfig = await fetchFirebaseConfig();
    if (firebaseConfig) {
        // Registrácia Service Workera
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/ios-service-worker.js')
            .then(function(registration) {
                console.log('Service Worker registered with scope:', registration.scope);

                // Poslanie Firebase konfigurácie do Service Workera
                if (registration.active) {
                    registration.active.postMessage({
                        firebaseConfig: firebaseConfig  // Posielame Firebase konfiguráciu do Service Workera
                    });
                }

                // Inicializácia Firebase na strane klienta
                const app = initializeApp(firebaseConfig);

                // Získanie Firebase Messaging inštancie
                const messaging = getMessaging(app);

                // Získanie FCM tokenu
                getToken(messaging, { vapidKey: publicVapidKey }).then((currentToken) => {
                    if (currentToken) {
                        console.log('FCM token:', currentToken);
                        sendTokenToServer(currentToken);  // Funkcia na odoslanie tokenu na server
                    } else {
                        console.log('Nebolo možné získať token.');
                    }
                }).catch((err) => {
                    console.error('Chyba pri získavaní tokenu:', err);
                });

                // Spracovanie správ v popredí
                onMessage(messaging, (payload) => {
                    console.log('Message received: ', payload);

                    const notificationTitle = payload.notification.title;
                    const notificationOptions = {
                        body: payload.notification.body,
                        icon: '/static/img/icon.png'
                    };

                    // Zobrazenie notifikácie priamo na stránke
                    new Notification(notificationTitle, notificationOptions);
                });
            }).catch(function(err) {
                console.error('Service Worker registration failed:', err);
            });
        }
    } else {
        console.error('Firebase configuration not available.');
    }
}

// Funkcia na odoslanie FCM tokenu na server
function sendTokenToServer(token) {
    fetch('/subscribe', {  // URL endpointu na back-ende
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // Ak používaš CSRF ochranu
        },
        body: JSON.stringify({ token: token })  // Posielame FCM token a/alebo ID používateľa
    })
    .then(response => response.json())
    .then(data => {
        console.log('Token uložený na serveri:', data);
    })
    .catch((error) => {
        console.error('Chyba pri odoslaní tokenu na server:', error);
    });
}

// Zavolaj funkciu na inicializáciu Firebase pri načítaní stránky
initializeFirebase();

// Skontroluj oprávnenie na notifikácie
Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
        console.log('Notifications granted');
    } else {
        console.error('Notifications denied');
    }
});
