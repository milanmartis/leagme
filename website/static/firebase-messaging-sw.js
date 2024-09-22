importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging.js');


    // Firebase konfigurácia
    const firebaseConfig = {
        apiKey: "AIzaSyCdvgoR_IQBnUk8cr1FstAGu66-o-fkSFM",
        authDomain: "leagme-2b3cd.firebaseapp.com",
        projectId: "leagme-2b3cd",
        storageBucket: "leagme-2b3cd.appspot.com",
        messagingSenderId: "192069980417",
        appId: "1:192069980417:web:10f7d96d0330865ff08b00",
        measurementId: "G-BJPEC0B7NG" // Pridajte, ak používate Analytics
    };

    // Inicializácia Firebase
    const app = firebase.initializeApp(firebaseConfig);
    const messaging = firebase.messaging();

    // Požiadajte o povolenie na odosielanie notifikácií
    messaging.requestPermission()
    .then(function() {
        console.log('Notification permission granted.');
        return messaging.getToken();
    })
    .then(function(token) {
        console.log('FCM Token:', token);
    })
    .catch(function(err) {
        console.log('Unable to get permission to notify.', err);
    });
