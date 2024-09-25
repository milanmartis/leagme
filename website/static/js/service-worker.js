self.addEventListener('push', event => {
    const data = event.data.json();
    console.log('Push notifikácia prijatá', data);

    const options = {
        body: data.body,
        icon: data.icon
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});