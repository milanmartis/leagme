self.addEventListener('message', function(event) {
    const firebaseConfig = event.data.firebaseConfig;

    if (firebaseConfig) {
        console.log('Loading Firebase scripts...');
        try {
            importScripts('/static/js/firebase-app.js');
            importScripts('/static/js/firebase-messaging.js');

            firebase.initializeApp(firebaseConfig);
            console.log('Firebase initialized in Service Worker with config:', firebaseConfig);

            const messaging = firebase.messaging();

            messaging.onBackgroundMessage(function(payload) {
                console.log('[Service Worker] Received background message: ', payload);

                const notificationTitle = payload.notification?.title || 'Default Title';
                const notificationOptions = {
                    body: payload.notification?.body || 'Default Body',
                    icon: '/static/img/icon.png'
                };

                self.registration.showNotification(notificationTitle, notificationOptions);
            });
        } catch (e) {
            console.error('Error loading Firebase scripts or initializing Firebase:', e);
        }
    } else {
        console.error('Firebase config not provided to Service Worker.');
    }
});

self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    console.log('Service Worker activated.');
    clients.claim();
});
