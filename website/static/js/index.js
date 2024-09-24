// VAPID public key
const publicVapidKey = vapidPublicKey;

// Detekcia iOS zariadenia
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Prihlásenie na odber push notifikácií
async function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator) {
        try {
            // Registrácia Service Workera
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker úspešne zaregistrovaný.');

            // Detekcia iOS a použitie Firebase Cloud Messaging (FCM) pre iOS
            if (isIOS()) {
                console.log('iOS zistené. Používa sa Firebase pre push notifikácie.');

                // Načítanie Firebase konfigurácie z backendu
                const response = await fetch('/get-firebase-config');
                if (!response.ok) {
                    throw new Error('Chyba pri načítavaní Firebase konfigurácie.');
                }
                const firebaseConfig = await response.json();

                // Inicializácia Firebase
                if (!firebase.apps.length) {
                    firebase.initializeApp(firebaseConfig);
                }

                // Registrácia pre Firebase Cloud Messaging (FCM)
                const messaging = firebase.messaging();
                try {
                    await messaging.requestPermission();
                    const fcmToken = await messaging.getToken();
                    console.log('FCM token:', fcmToken);

                    // Odoslanie FCM tokenu na backend
                    await fetch('/subscribe', {
                        method: 'POST',
                        body: JSON.stringify({ token: fcmToken }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken // Pridaj CSRF token, ak je potrebný pre backend
                        }
                    });

                    console.log('FCM token odoslaný na server.');
                } catch (error) {
                    console.error('Chyba pri získavaní FCM tokenu:', error);
                }

            } else {
                // Požiadať používateľa o povolenie na zobrazovanie push notifikácií (Web Push API pre ostatné platformy)
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    throw new Error('Povolenie na push notifikácie nebolo udelené.');
                }

                // Prihlásenie na odber push notifikácií
                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true, // Uistíme sa, že notifikácie budú viditeľné pre používateľa
                    applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
                });

                console.log('Subscription údaje:', subscription);

                // Odoslanie subscription údajov na backend
                const response = await fetch('/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken // Pridaj CSRF token do hlavičky, ak je potrebný pre backend
                    }
                });

                if (!response.ok) {
                    throw new Error('Chyba pri odosielaní subscription na server.');
                }

                console.log('Prihlásenie na push notifikácie prebehlo úspešne.');
            }

        } catch (error) {
            alert('kuk zleeee');
            console.error('Prihlásenie na push notifikácie zlyhalo:', error);
        }
    } else {
        console.error('Service Worker nie je podporovaný v tomto prehliadači.');
    }
}

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

// Overíme, či prehliadač podporuje Push API a spustíme proces prihlásenia na notifikácie
window.addEventListener('load', () => {
    subscribeToPushNotifications();
});
