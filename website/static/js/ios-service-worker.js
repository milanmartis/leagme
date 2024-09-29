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

        // Spracovanie prichádzajúcich push notifikácií
        messaging.onBackgroundMessage(function(payload) {
            console.log('[ios-service-worker.js] Received background message ', payload);

            const notificationTitle = payload.notification.title;
            const notificationOptions = {
                body: payload.notification.body,
                icon: '/your-icon.png',  // Definuj cestu k tvojej ikone pre notifikáciu
                badge: '/your-badge-icon.png'  // Badge ikona (odporúča sa pre iOS)
            };

            // Zobrazenie notifikácie
            self.registration.showNotification(notificationTitle, notificationOptions);
        });
    } else {
        console.error('Firebase config not provided to Service Worker.');
    }
});
