// VAPID public key
const publicVapidKey = vapidPublicKey;
// Prihlásenie na odber push notifikácií
async function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator) {
        try {
            // Registrácia service workera
            const registration = await navigator.serviceWorker.register('/service-worker.js');
            console.log('Service Worker registrovaný.');

            // Požiadať používateľa o povolenie na zobrazovanie push notifikácií
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                throw new Error('Povolenie na push notifikácie nebolo udelené.');
            }

            // Prihlásenie na odber push notifikácií
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
            });

            // Odoslanie subscription údajov na backend
            await fetch('/subscribe', {
                method: 'POST',
                body: JSON.stringify(subscription),
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('Prihlásenie na push notifikácie prebehlo úspešne.');
        } catch (error) {
            console.error('Prihlásenie na push notifikácie zlyhalo.', error);
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

// Zavolať funkciu pri načítaní stránky
subscribeToPushNotifications();