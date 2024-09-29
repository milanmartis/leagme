import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";  // Pridaj Firebase App SDK
import { getMessaging, getToken } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";
import { onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";

// Získaj inštanciu messaging
const messaging = getMessaging();

// Spracovanie správ v popredí
onMessage(messaging, (payload) => {
    console.log('Message received. ', payload);

    // Prispôsobenie zobrazenia notifikácie
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/static/img/icon.png'
    };

    // Zobrazenie notifikácie priamo na stránke
    new Notification(notificationTitle, notificationOptions);
});
const publicVapidKey = vapidPublicKey;  // Nahradiť vlastným VAPID kľúčom
Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
        console.log('Notifications granted');
    } else {
        console.error('Notifications denied');
    }
});

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/ios-service-worker.js')
    .then(function(registration) {
        console.log('Service Worker registered with scope:', registration.scope);
    }).catch(function(err) {
        console.error('Service Worker registration failed:', err);
    });
}
// Funkcia pre načítanie Firebase konfigurácie z backendu
async function fetchFirebaseConfig() {
    try {
        const response = await fetch('/get-firebase-config');  // Tu načítaš konfiguráciu zo svojho servera
        if (!response.ok) {
            throw new Error('Failed to fetch Firebase config.');
        }
        const firebaseConfig = await response.json();
        return firebaseConfig;
    } catch (error) {
        console.error('Error fetching Firebase config:', error);
    }
}

// Funkcia pre inicializáciu Firebase s dynamickou konfiguráciou
async function initializeFirebase() {
    const firebaseConfig = await fetchFirebaseConfig();
    if (firebaseConfig) {
        // Inicializácia Firebase pomocou dynamickej konfigurácie
        initializeApp(firebaseConfig);  // Použi initializeApp z Firebase App SDK

        // Získanie Firebase Cloud Messaging tokenu
        const messaging = getMessaging();
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


// async function sendPushNotification(fcmToken, title, body) {
//     try {
//         const response = await fetch('/send-notification', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 fcm_token: fcmToken,
//                 title: title,
//                 body: body
//             })
//         });

//         const data = await response.json();
//         console.log('Odoslanie notifikácie:', data);
//     } catch (error) {
//         console.error('Chyba pri odosielaní notifikácie:', error);
//     }
// }

