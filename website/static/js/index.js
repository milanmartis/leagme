import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";
const publicVapidKey = vapidPublicKey;  // Nahraď vlastným VAPID kľúčom

// Tvoja Firebase konfigurácia
const firebaseConfig = {
    apiKey: "AIzaSyDpiYa-ePpi1dS1OrLO5EhIM0hmMMNUVio",
    authDomain: "leagme-project.firebaseapp.com",
    projectId: "leagme-project",
    storageBucket: "leagme-project.appspot.com",
    messagingSenderId: "145118008865",
    appId: "1:145118008865:web:158b335f6a2d06e6883560"
};

// Inicializácia Firebase a registrácia Service Workera
async function initializeFirebase() {
    // Inicializácia Firebase priamo na klientovi
    const app = initializeApp(firebaseConfig);

    // Registrácia Service Workera
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/ios-service-worker.js')
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);

            // Získanie Firebase Messaging inštancie s registrovaným Service Workerom
            const messaging = getMessaging(app);

            // Získanie FCM tokenu pomocou už registrovaného Service Workera
            getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration }).then((currentToken) => {
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
