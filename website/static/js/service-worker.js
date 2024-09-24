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


self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};

    // Zvýšenie počtu neprečítaných notifikácií
    getUnreadCount().then(currentCount => {
        const newCount = currentCount + 1;
        saveUnreadCount(newCount).then(() => {
            // Aktualizácia odznaku pomocou Badging API
            if ('setAppBadge' in navigator) {
                navigator.setAppBadge(newCount).catch(error => {
                    console.error('Chyba pri nastavovaní odznaku:', error);
                });
            }

            const options = {
                body: data.body || 'Nová správa!',
                icon: '/static/icon.png'
            };

            // Zobrazenie push notifikácie
            self.registration.showNotification(data.title || 'Nová notifikácia', options);
        });
    });
});