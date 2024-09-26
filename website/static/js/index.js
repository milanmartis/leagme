// VAPID public key
const publicVapidKey = vapidPublicKey;

// Function to detect iOS devices
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Function to check if notifications are supported
function checkNotificationSupport() {
    if (!("Notification" in window)) {
        console.error("This browser does not support notifications.");
        return false;
    }
    return true;
}

// Request Notification Permission
async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        console.log("Notification permission status:", permission);
        return permission === 'granted';
    } catch (error) {
        console.error('Error while requesting notification permission:', error);
        return false;
    }
}

// Function to register service worker and request FCM token
async function subscribeToPushNotifications() {
    if (!checkNotificationSupport()) {
        console.error('Browser does not support notifications.');
        return;
    }

    if ('serviceWorker' in navigator) {
        try {
            // Register service worker for Web Push
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker registered successfully.');

            // iOS detection and Firebase Cloud Messaging for iOS
            if (isIOS()) {
                console.log('iOS detected. Using Firebase for push notifications.');

                // Request permission for notifications
                const permissionGranted = await requestNotificationPermission();
                if (!permissionGranted) {
                    console.error('Notification permission denied on iOS.');
                    return;
                }

                // Fetch Firebase configuration from backend
                const response = await fetch('/get-firebase-config');
                if (!response.ok) {
                    throw new Error('Failed to fetch Firebase configuration.');
                }
                const firebaseConfig = await response.json();

                // Initialize Firebase
                if (!firebase.apps.length) {
                    firebase.initializeApp(firebaseConfig);
                }

                const messaging = firebase.messaging();

                try {
                    // Get FCM token (VAPID key for Web Push)
                    const fcmToken = await messaging.getToken({
                        vapidKey: publicVapidKey,
                        serviceWorkerRegistration: registration
                    });

                    if (fcmToken) {
                        alert(`FCM Token: ${fcmToken}`);
                        console.log('FCM Token received:', fcmToken);

                        // Send FCM token to the backend
                        await fetch('/subscribe', {
                            method: 'POST',
                            body: JSON.stringify({ token: fcmToken }),
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            }
                        });
                        console.log('FCM token sent to server.');
                    } else {
                        console.error('Failed to get FCM token.');
                    }
                } catch (error) {
                    console.error('Error while getting FCM token:', error);
                }
            } else {
                // Handle Web Push for other platforms (non-iOS)
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    console.error('Push notifications permission not granted.');
                    return;
                }

                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
                });

                console.log('Subscription data:', subscription);

                // Send subscription data to backend
                const response = await fetch('/subscribe', {
                    method: 'POST',
                    body: JSON.stringify(subscription),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });

                if (!response.ok) {
                    console.error('Failed to send subscription to server.');
                } else {
                    console.log('Successfully subscribed to push notifications.');
                }
            }
        } catch (error) {
            console.error('Push notifications subscription failed:', error);
        }
    } else {
        console.error('Service Worker not supported in this browser.');
    }
}

// Function to convert VAPID key to Uint8Array
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

// Attach the event listener to a button
document.getElementById('enableNotificationsButton').addEventListener('click', async () => {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
        console.log('Permission granted.');
        await subscribeToPushNotifications();
    } else {
        console.log('Push notifications not granted.');
    }
});
