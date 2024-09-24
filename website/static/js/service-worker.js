self.addEventListener('push', event => {
    const data = event.data.json();
    console.log('Push notifikácia prijatá:', data);

    const options = {
        title: "kuk",
        body: data.body,
        icon: '/static/img/icon.png'  // Cesta k ikonke notifikácie
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();  // Zatvorí notifikáciu
    event.waitUntil(
        clients.openWindow('/')  // Otvorí aplikáciu, keď používateľ klikne na notifikáciu
    );
});
