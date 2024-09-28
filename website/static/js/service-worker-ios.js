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
