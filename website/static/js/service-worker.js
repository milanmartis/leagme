// Otvorenie alebo vytvorenie IndexedDB databázy
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('notifications-db', 1);
        request.onupgradeneeded = event => {
            const db = event.target.result;
            db.createObjectStore('notifications', { keyPath: 'id' });
        };
        request.onsuccess = event => {
            resolve(event.target.result);
        };
        request.onerror = event => {
            reject('Error opening IndexedDB');
        };
    });
}

// Uloženie počtu neprečítaných notifikácií do IndexedDB
function saveUnreadCount(count) {
    return openDatabase().then(db => {
        const tx = db.transaction('notifications', 'readwrite');
        const store = tx.objectStore('notifications');
        store.put({ id: 1, count: count });
        return tx.complete;
    });
}

// Získanie počtu neprečítaných notifikácií z IndexedDB
function getUnreadCount() {
    return openDatabase().then(db => {
        return new Promise((resolve, reject) => {
            const tx = db.transaction('notifications', 'readonly');
            const store = tx.objectStore('notifications');
            const request = store.get(1);
            request.onsuccess = () => {
                resolve(request.result ? request.result.count : 0);
            };
            request.onerror = () => {
                reject('Error fetching unread count');
            };
        });
    });
}

// Listener pre 'push' udalosť - spracovanie prijatej push správy
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};

    // Zvýšenie počtu neprečítaných notifikácií
    getUnreadCount().then(currentCount => {
        const newCount = currentCount + 1;

        // Uloženie nového počtu do IndexedDB
        saveUnreadCount(newCount).then(() => {
            // Aktualizácia odznaku pomocou Badging API
            if ('setAppBadge' in navigator) {
                navigator.setAppBadge(newCount).catch(error => {
                    console.error('Chyba pri nastavovaní odznaku:', error);
                });
            }

            // Zobrazenie push notifikácie
            const options = {
                body: data.body || 'Nová správa!',
                icon: data.icon || '/static/img/icon.png',
                data: {
                    url: data.url || '/' // URL, ktorá sa otvorí po kliknutí na notifikáciu
                }
            };

            event.waitUntil(
                self.registration.showNotification(data.title || 'Nová notifikácia', options)
            );
        });
    });
});

// Listener pre 'notificationclick' udalosť - spracovanie kliknutia na notifikáciu
self.addEventListener('notificationclick', event => {
    event.notification.close(); // Zatvorenie notifikácie

    // Otvorenie okna alebo zameranie na už existujúce okno
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            for (let client of windowClients) {
                if (client.url === event.notification.data.url && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});

// Listener pre 'notificationclose' udalosť - spracovanie zatvorenia notifikácie
self.addEventListener('notificationclose', event => {
    console.log('Notifikácia bola zatvorená.');
});

// Odstránenie odznaku pri obnovení počtu neprečítaných správ
self.addEventListener('message', event => {
    if (event.data === 'reset-badge') {
        if ('clearAppBadge' in navigator) {
            navigator.clearAppBadge().catch(error => {
                console.error('Chyba pri odstraňovaní odznaku:', error);
            });
        }

        // Resetovanie počtu neprečítaných notifikácií
        saveUnreadCount(0);
    }
});
