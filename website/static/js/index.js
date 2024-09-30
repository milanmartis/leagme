import { initializeApp } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/9.13.0/firebase-messaging.js";

const publicVapidKey = vapidPublicKey;  // Nahraď vlastným VAPID kľúčom

// Funkcia pre načítanie Firebase konfigurácie z backendu
async function fetchFirebaseConfig() {
    try {
        const response = await fetch('/get-firebase-config');
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
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/ios-service-worker.js')
            .then(function(registration) {
                console.log('Service Worker registered with scope:', registration.scope);

                if (registration.active) {
                    registration.active.postMessage({
                        firebaseConfig: firebaseConfig
                    });
                }

                const app = initializeApp(firebaseConfig);
                const messaging = getMessaging(app);

                // Získanie FCM tokenu
                getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration })
                    .then((currentToken) => {
                        if (currentToken) {
                            console.log('FCM token:', currentToken);
                            sendTokenToServer(currentToken);
                        } else {
                            console.log('Nebolo možné získať token.');
                        }
                    })
                    .catch((err) => {
                        console.error('Chyba pri získavaní tokenu:', err);
                    });

                // Spracovanie správ v popredí (prijatých keď je aplikácia otvorená)
                onMessage(messaging, (payload) => {
                    console.log('Message received: ', payload);

                    const notificationTitle = payload.notification.title;
                    const notificationOptions = {
                        body: payload.notification.body,
                        icon: '/static/img/icon.png'
                    };

                    // Zobrazenie notifikácie
                    new Notification(notificationTitle, notificationOptions);
                });
            })
            .catch(function(err) {
                console.error('Service Worker registration failed:', err);
            });
        }
    } else {
        console.error('Firebase configuration not available.');
    }
}

// Funkcia na odoslanie FCM tokenu na server
function sendTokenToServer(token) {
    fetch('/subscribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ token: token })
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
