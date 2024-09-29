// Príjem Firebase konfigurácie od hlavného vlákna
self.addEventListener('message', function(event) {
    const firebaseConfig = event.data.firebaseConfig;

    if (firebaseConfig) {
        // Import Firebase scripts for messaging
        importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js');
        importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js');

        // Inicializácia Firebase pomocou dynamicky prijatej konfigurácie
        firebase.initializeApp(firebaseConfig);
        console.log('Firebase initialized in Service Worker with config:', firebaseConfig);

        // Inicializácia Firebase Messaging
        const messaging = firebase.messaging();

        // Spracovanie prichádzajúcich push notifikácií na pozadí
        messaging.onBackgroundMessage(function(payload) {
            console.log('[firebase-messaging-sw.js] Received background message ', payload);
        
            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: '/static/img/icon.png'
            };
        
            self.registration.showNotification(notificationTitle, notificationOptions);
        });
    } else {
        console.error('Firebase config not provided to Service Worker.');
    }
});

// Zabezpečenie, že Service Worker bude pripravený prijímať konfiguračné údaje
self.addEventListener('install', event => {
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    clients.claim();
});
