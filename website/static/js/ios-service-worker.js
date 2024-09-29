// Firebase konfigurácia priamo v Service Worker
const firebaseConfig = {
    apiKey: "AIzaSyDpiYa-ePpi1dS1OrLO5EhIM0hmMMNUVio",
    authDomain: "leagme-project.firebaseapp.com",
    projectId: "leagme-project",
    storageBucket: "leagme-project.appspot.com",
    messagingSenderId: "145118008865",
    appId: "1:145118008865:web:158b335f6a2d06e6883560"
};

// Načítanie Firebase SDK skriptov a inicializácia priamo v Service Worker
try {
    console.log('Loading Firebase scripts...');
    importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js');
    importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js');

    // Inicializácia Firebase v Service Worker
    firebase.initializeApp(firebaseConfig);
    console.log('Firebase initialized in Service Worker with config:', firebaseConfig);

    const messaging = firebase.messaging();

    // Spracovanie správ na pozadí (Background Message Handling)
    messaging.onBackgroundMessage(function(payload) {
        console.log('[Service Worker] Received background message: ', payload);

        const notificationTitle = payload.notification?.title || 'Default Title';
        const notificationOptions = {
            body: payload.notification?.body || 'Default Body',
            icon: '/static/img/icon.png'
        };

        // Zobrazenie notifikácie
        self.registration.showNotification(notificationTitle, notificationOptions);
    });

} catch (e) {
    console.error('Error loading Firebase scripts or initializing Firebase:', e);
}

// Spracovanie inštalácie Service Workera
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    self.skipWaiting();  // Aktivácia SW ihneď bez čakania na ukončenie starých SW
});

// Spracovanie aktivácie Service Workera
self.addEventListener('activate', event => {
    console.log('Service Worker activated.');
    clients.claim();  // Prevzatie kontroly nad stránkou bez potreby znovu načítania
});
