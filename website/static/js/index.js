import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/ios-service-worker.js')
    .then((registration) => {
        console.log('Service Worker registered with scope:', registration.scope);
    }).catch((error) => {
        console.error('Service Worker registration failed:', error);
    });
}

const publicVapidKey = vapidPublicKey;  // Nahradiť vlastným VAPID kľúčom
const user_Id = userId;
const firebaseConfig = await fetchFirebaseConfig();
const app = initializeApp(firebaseConfig);

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

const messaging = getMessaging(app);

// Získanie FCM tokenu
async function requestPermissionAndToken() {
    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            console.log('Permission granted for notifications');
            const currentToken = await getToken(messaging, { vapidKey: publicVapidKey });
            if (currentToken) {
                console.log('FCM Token:', currentToken);
                // Ulož token na server pre ďalšie použitie
                sendTokenToServer(currentToken);
            } else {
                console.log('No registration token available. Request permission to generate one.');
            }
        } else {
            console.log('Permission denied for notifications');
        }
    } catch (error) {
        console.error('An error occurred while retrieving token. ', error);
    }
}

// Funkcia na odoslanie tokenu na server
function sendTokenToServer(token) {
    fetch('/subscribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,  // Ak používaš CSRF ochranu
        },
        body: JSON.stringify({ token: token, user_id: user_Id })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Token uložený na serveri:', data);
    })
    .catch((error) => {
        console.error('Chyba pri ukladaní tokenu:', error);
    });
}

// Zavolaj funkciu na získanie povolenia a tokenu
requestPermissionAndToken();