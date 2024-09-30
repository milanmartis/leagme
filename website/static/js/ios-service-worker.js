self.addEventListener('install', function(event) {
    console.log('Service Worker installing...');
    try {
        // Import Firebase scripts už počas inštalácie
        importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js');
        importScripts('https://www.gstatic.com/firebasejs/8.10.0/firebase-messaging.js');
        self.skipWaiting();
    } catch (e) {
        console.error('Failed to load Firebase scripts:', e);
    }
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker activated.');
    clients.claim();
});

self.addEventListener('message', function(event) {
    const firebaseConfig = event.data.firebaseConfig;
    if (firebaseConfig) {
        try {
            if (firebase.apps.length === 0) {
                firebase.initializeApp(firebaseConfig);
                console.log('Firebase initialized in Service Worker with config:', firebaseConfig);
            } else {
                console.log('Firebase App already initialized.');
            }

            const messaging = firebase.messaging();

            messaging.onBackgroundMessage(function(payload) {
                console.log('[Service Worker] Received background message:', payload);

                const notificationTitle = payload.notification.title || 'Default Title';
                const notificationOptions = {
                    body: payload.notification.body || 'Default Body',
                    icon: '/static/img/icon.png'
                };

                self.registration.showNotification(notificationTitle, notificationOptions);
            });
        } catch (e) {
            console.error('Error initializing Firebase:', e);
        }
    } else {
        console.error('Firebase config not provided to Service Worker.');
    }
});

// Pridanie event handlerov pre 'push', 'pushsubscriptionchange' a 'notificationclick'
self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push received.');
    if (event.data) {
        const payload = event.data.json();
        const notificationTitle = payload.notification.title || 'Push Notification';
        const notificationOptions = {
            body: payload.notification.body || 'You have a new message!',
            icon: '/static/img/icon.png'
        };

        event.waitUntil(
            self.registration.showNotification(notificationTitle, notificationOptions)
        );
    }
});

self.addEventListener('pushsubscriptionchange', function(event) {
    console.log('[Service Worker] Subscription change detected.');
    // Tu môžete implementovať logiku na obnovenie subscription.
});

self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click received.');
    event.notification.close();

    // Otvorenie alebo fokusovanie okna po kliknutí na notifikáciu
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(clientList) {
            if (clientList.length > 0) {
                return clientList[0].focus();
            }
            return clients.openWindow('/');
        })
    );
});
