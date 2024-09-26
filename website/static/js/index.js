// VAPID public key
const publicVapidKey = vapidPublicKey;

// Detekcia iOS zariadenia
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Funkcia na registráciu Service Workera a získanie FCM tokenu
async function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator) {
        try {
            // Registrácia Service Workera pre Web Push
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

                // Získanie FCM tokenu pre iOS
                const messaging = firebase.messaging();
                try {
                    const fcmToken = await messaging.getToken({
                        vapidKey: publicVapidKey,
                        serviceWorkerRegistration: registration
                    });
                    
                    if (fcmToken) {
                        alert(fcmToken);

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
                    } else {
                        console.error('Nebolo možné získať FCM token.');
                    }
                } catch (error) {
                    alert("chyba token");
                    console.error('Chyba pri získavaní FCM tokenu:', error);
                }
            } else {
                // Požiadať používateľa o povolenie na zobrazovanie push notifikácií (Web Push API pre ostatné platformy)
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    throw new Error('Povolenie na push notifikácie nebolo udelené.');
                }

                // Prihlásenie na odber push notifikácií pre Web Push API
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

// Funkcia, ktorá sa zavolá po kliknutí na tlačidlo
document.getElementById('enableNotificationsButton').addEventListener('click', async () => {
    const permission = await Notification.requestPermission();
      
    if (permission === 'granted') {
        // Ak užívateľ povolil push notifikácie, prihlásime ho na odber
        console.log('Povolenie udelené');
        subscribeToPushNotifications();
    } else {
        // Ak povolenie nebolo udelené alebo bolo odmietnuté
        console.log('Push notifikácie neboli povolené');
    }
});
