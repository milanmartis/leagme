self.addEventListener('push', function(event) {
    const data = event.data.json();
    console.log('Push received:', data);

    const options = {
        body: data.body,
        icon: '/static/icons/icon-192x192.png', // Set your icon path
        badge: '/static/icons/icon-96x96.png'
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    event.waitUntil(
        clients.openWindow('/')  // Open your app or a specific page when clicked
    );
});


// Komunikácia so stránkou na resetovanie odznaku pri otvorení stránky
clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clients => {
    if (clients.length) {
        clients[0].postMessage('reset-badge'); // Posielame správu stránke, že chceme resetovať odznak
    }
});


// Pri načítaní stránky resetujeme počítadlo neprečítaných správ
window.addEventListener('load', async () => {
    await resetUnreadCount(); // Resetuje počítadlo pri načítaní stránky
});