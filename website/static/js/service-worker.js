self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};

    // Nastavenie predvolených hodnôt pre notifikáciu, ak niektoré údaje chýbajú
    const options = {
        body: data.body || 'Nová správa!',
        icon: data.icon || '/static/img/icon.png',
        tag: data.tag || 'default-tag', // Tag pre zlúčenie notifikácií
        actions: [
            { action: 'view', title: 'Zobraziť' },
            { action: 'dismiss', title: 'Zatvoriť' }
        ],
        data: {
            url: data.url || '/' // URL na otvorenie po kliknutí na notifikáciu
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'Nová notifikácia', options)
    );
});

// Spracovanie kliknutia na notifikáciu
self.addEventListener('notificationclick', event => {
    event.notification.close(); // Zatvorenie notifikácie po kliknutí

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
