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
            // Skontroluj, či Firebase app už existuje
            if (firebase.apps.length === 0) {
                firebase.initializeApp(firebaseConfig);
                console.log('Firebase initialized in Service Worker with config:', firebaseConfig);
            } else {
                console.log('Firebase App already initialized.');
            }

            const messaging = firebase.messaging();

            messaging.onBackgroundMessage(function(payload) {
                console.log('[ios-service-worker.js] Received background message', payload);

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
