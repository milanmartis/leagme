
const publicVapidKey = vapidPublicKey;  // Nahradiť vlastným VAPID kľúčom
const user_Id = userId;

// Register Service Worker and request push notifications
async function registerServiceWorkerAndSubscribe() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        try {
            const registration = await navigator.serviceWorker.register('/static/js/service-worker-ios.js');
            console.log('Service Worker successfully registered:', registration);

            // Check if user is already subscribed
            const existingSubscription = await registration.pushManager.getSubscription();
            if (existingSubscription) {
                console.log('User is already subscribed to notifications:', existingSubscription);
                // You might want to check with your server if this subscription is already stored
                return existingSubscription;
            }

            // Ask for permission to send notifications
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                throw new Error('Permission for notifications was not granted');
            }

            // Subscribe to Push Notifications with VAPID key
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(publicVapidKey)  // VAPID public key
            });

            console.log('User subscribed:', subscription);
            await sendSubscriptionToServer(subscription);

            return subscription;

        } catch (error) {
            console.error('Failed to subscribe to push notifications:', error);
        }
    } else {
        console.error('Push messaging is not supported in this browser');
    }
}

// Convert VAPID key to Uint8Array
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

// Send the subscription to the server
async function sendSubscriptionToServer(subscription) {
    const data = {
        user_id: user_Id,
        subscription: subscription,
    };
    const response = await fetch('/subscribe', {
        method: 'POST',
        body: JSON.stringify(subscription),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken  
        }
    });

    if (!response.ok) {
        console.error('Failed to send subscription to server');
    } else {
        console.log('Subscription successfully sent to the server');
    }
}

// On page load, register service worker and subscribe
document.addEventListener('DOMContentLoaded', async () => {
    await registerServiceWorkerAndSubscribe();
});
