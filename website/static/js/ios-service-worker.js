self.addEventListener('install', function(event) {
    console.log('Service Worker installing...');
    try {
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

// Inicializácia Firebase okamžite
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

// Event handler pre push
self.addEventListener('push', function(event) {
    console.log('[Service Worker] Push event received.');
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

// Event handler pre pushsubscriptionchange
self.addEventListener('pushsubscriptionchange', function(event) {
    console.log('[Service Worker] Push subscription change detected.');
    // Riešenie pre obnovenie alebo aktualizáciu subscription
});

// Event handler pre notificationclick
self.addEventListener('notificationclick', function(event) {
    console.log('[Service Worker] Notification click received.');
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(clientList) {
            if (clientList.length > 0) {
                return clientList[0].focus();
            }
            return clients.openWindow('/');
        })
    );
});
