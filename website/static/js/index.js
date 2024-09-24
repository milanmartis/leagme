// const publicVapidKey = vapidPublicKey;

document.addEventListener('DOMContentLoaded', () => {
    const notificationModal = document.getElementById('notificationModal');
    notificationModal.style.display = 'block'; // Zobrazí modálne okno

    document.getElementById('allowNotificationsButton').addEventListener('click', async () => {
        await requestNotificationPermission();
        notificationModal.style.display = 'none'; // Skryje modálne okno po odpovedi
    });

    document.getElementById('denyNotificationsButton').addEventListener('click', () => {
        notificationModal.style.display = 'none'; // Skryje modálne okno, ak používateľ odmietne
    });
});

async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            // Registrácia service workera a prihlásenie na odber notifikácií
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            const publicVapidKey = await fetchPublicVapidKey();

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
            });

            // Odoslanie subscription na backend
            await fetch('/subscribe', {
                method: 'POST',
                body: JSON.stringify(subscription),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken                 }
            });

            console.log('Používateľ je prihlásený na push notifikácie');
        } else {
            console.log('Používateľ odmietol push notifikácie');
        }
    } catch (error) {
        console.error('Chyba pri prihlásení na notifikácie:', error);
    }
}

async function fetchPublicVapidKey() {
    const response = await fetch('/vapid-public-key');
    const data = await response.json();
    return data.publicVapidKey;
}

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