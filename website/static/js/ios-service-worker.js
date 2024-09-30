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

try {
    // Inicializácia Firebase v Service Worker
    const firebaseConfig = {
        apiKey: "AIzaSyDpiYa-ePpi1dS1OrLO5EhIM0hmMMNUVio",
        authDomain: "leagme-project.firebaseapp.com",
        projectId: "leagme-project",
        storageBucket: "leagme-project.appspot.com",
        messagingSenderId: "145118008865",
        appId: "1:145118008865:web:158b335f6a2d06e6883560"
    };

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
    console.error('Error initializing Firebase in Service Worker:', e);
}

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
    // Implement logic to handle subscription change, if needed
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
