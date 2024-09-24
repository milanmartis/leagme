// VAPID public key
const publicVapidKey = vapidPublicKey;

// Prihlásenie na odber push notifikácií
async function subscribeToPushNotifications() {
    if ('serviceWorker' in navigator) {
        try {
            // Registrácia Service Workera
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker úspešne zaregistrovaný.');

            // Požiadať používateľa o povolenie na zobrazovanie push notifikácií
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

// Overíme, či prehliadač podporuje Push API a spustíme proces prihlásenia na notifikácie
window.addEventListener('load', () => {
    subscribeToPushNotifications();
});
