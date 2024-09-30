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

// Funkcia pre získanie web push subscription
async function subscribeUserToPush(registration) {
    try {
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(publicVapidKey) // Konverzia VAPID kľúča na pole uint8
        });
        return subscription;
    } catch (error) {
        console.error('Failed to subscribe the user: ', error);
    }
}

// Konverzia VAPID kľúča z base64
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Inicializácia Firebase a registrácia Service Workera
async function initializeFirebase() {
    const firebaseConfig = await fetchFirebaseConfig();
    if (firebaseConfig) {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/ios-service-worker.js')
                .then(async function (registration) {
                    console.log('Service Worker registered with scope:', registration.scope);

                    const app = initializeApp(firebaseConfig);
                    const messaging = getMessaging(app);

                    // Pokus o vymazanie starého tokenu
                    try {
                        const oldToken = await getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration });
                        if (oldToken) {
                            console.log('Deleting old FCM token:', oldToken);
                            await messaging.deleteToken(oldToken);
                        }
                    } catch (error) {
                        console.error('Error deleting old token:', error);
                    }

                    // Získanie nového FCM tokenu
                    const currentToken = await getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration });
                    if (currentToken) {
                        console.log('New FCM token:', currentToken);
                        // Odoslanie tokenu a subscription na server
                        const subscription = await subscribeUserToPush(registration);
                        sendSubscriptionToServer(currentToken, subscription);
                    } else {
                        console.log('Nebolo možné získať token.');
                    }

                    // Spracovanie správ
                    onMessage(messaging, (payload) => {
                        console.log('Message received: ', payload);
                    });
                }).catch(function (err) {
                    console.error('Service Worker registration failed:', err);
                });
        }
    } else {
        console.error('Firebase configuration not available.');
    }
}

// Funkcia na odoslanie FCM tokenu a subscription na server
function sendSubscriptionToServer(token, subscription) {
    const subscriptionData = {
        token: token,
        endpoint: subscription.endpoint,
        keys: {
            p256dh: subscription.keys.p256dh,
            auth: subscription.keys.auth
        }
    };

    fetch('/subscribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(subscriptionData)
    })
        .then(response => response.json())
        .then(data => {
            console.log('Subscription uložená na serveri:', data);
        })
        .catch((error) => {
            console.error('Chyba pri odoslaní subscription na server:', error);
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
