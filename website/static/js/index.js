import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";

const publicVapidKey = vapidPublicKey;  // Nahradiť vlastným VAPID kľúčom
const user_Id = userId;

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

// Funkcia pre inicializáciu Firebase a registráciu Service Worker
async function initializeFirebase() {
    const firebaseConfig = await fetchFirebaseConfig();
    if (firebaseConfig) {
        // Inicializácia Firebase pomocou získanej konfigurácie
        const app = initializeApp(firebaseConfig);
        console.log('Firebase initialized successfully');

        // Registrácia Service Worker pre Web Push a FCM
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
                console.log('Service Worker registered successfully:', registration);

                // Detekcia platformy (iOS alebo iné zariadenia)
                if (isIOS()) {
                    // Pre iOS použijeme Firebase Cloud Messaging
                } else {
                    // Pre iné zariadenia (Android, desktop) použijeme Web Push API
                    await handleIOSPushNotifications(app, registration);
                    // await handleWebPushNotifications(registration);
                }
            } catch (error) {
                console.error('Service Worker registration failed:', error);
            }
        } else {
            console.log('Service Worker nie je podporovaný v tomto prehliadači.');
        }
    } else {
        console.error('Firebase initialization failed');
    }
}

// Funkcia pre spracovanie FCM tokenu pre iOS
async function handleIOSPushNotifications(app, registration) {
    const messaging = getMessaging(app);

    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            // Získanie FCM tokenu pre iOS zariadenia
            const token = await getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration });
            if (token) {
                console.log('FCM Token (iOS):', token);
                saveTokenToServer(user_Id, token);  // Uloženie FCM tokenu na server
            } else {
                console.log('Nie je možné získať token pre iOS.');
            }
        } else {
            console.error('Permission denied for iOS push notifications.');
        }
    } catch (error) {
        console.error('Chyba pri získavaní tokenu pre iOS:', error);
    }
}

// Funkcia pre spracovanie Web Push subscription pre iné zariadenia
async function handleWebPushNotifications(registration) {
    try {
        // Získaj existujúce predplatné (subscription)
        const existingSubscription = await registration.pushManager.getSubscription();
        
        // Ak predplatné existuje, odhlás ho
        if (existingSubscription) {
            console.log('Existing subscription found. Unsubscribing...');
            await existingSubscription.unsubscribe();
            console.log('Successfully unsubscribed existing subscription.');
        }

        // Získaj povolenie na push notifikácie
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            // Prihlásenie na odber push notifikácií cez Web Push API s novým VAPID kľúčom

            const existingSubscription = await registration.pushManager.getSubscription();
            if (existingSubscription) {
                console.log('Odhlasovanie existujúceho predplatného...');
                await existingSubscription.unsubscribe();
                console.log('Odhlásenie úspešné');
            }

            // Prihlásenie nového predplatného
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
            });
            console.log('Web Push Subscription:', subscription);
            const p256dhKey = subscription.getKey('p256dh');
            const authKey = subscription.getKey('auth');

            if (p256dhKey && authKey) {
                const p256dhBase64 = arrayBufferToBase64(p256dhKey);
                const authBase64 = arrayBufferToBase64(authKey);
                
                saveSubscriptionToServer(user_Id, subscription.endpoint, p256dhBase64, authBase64);  // Uloženie subscription údajov na server
                console.log('p256dh (base64):', p256dhBase64);
                console.log('auth (base64):', authBase64);
                
                // Môžete ich teraz uložiť na server alebo použiť v iných častiach kódu
            }
            function arrayBufferToBase64(buffer) {
                const bytes = new Uint8Array(buffer);
                let binary = '';
                for (let i = 0; i < bytes.byteLength; i++) {
                    binary += String.fromCharCode(bytes[i]);
                }
                return btoa(binary);
            }


        } else {
            console.error('Permission denied for Web Push notifications.');
        }
    } catch (error) {
        console.error('Chyba pri spracovaní Web Push subscription:', error);
    }
}

// Funkcia pre ukladanie Web Push subscription údajov na server
function saveSubscriptionToServer(user_Id, subscriptionEndpoint, p256dh, auth) {
    const url = '/subscribe';

    const data = {
        user_id: user_Id,
        endpoint: subscriptionEndpoint,
        p256dh: p256dh,
        auth: auth,
        typ: '1'
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // CSRF token na ochranu pred útokmi
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Web Push subscription sent to server:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Funkcia pre ukladanie tokenu na server (pre iOS FCM)
function saveTokenToServer(user_Id, token) {
    const url = '/subscribe';

    const data = {
        user_id: user_Id,
        auth: token,  // Token je poslaný ako 'auth', aby zodpovedal backendu
        typ: '2'
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  // CSRF token na ochranu pred útokmi
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('FCM token sent to server:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

// Funkcia na detekciu iOS zariadení
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Funkcia na konverziu VAPID kľúča na Uint8Array
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

// Spustenie inicializácie Firebase pri načítaní stránky
initializeFirebase();
