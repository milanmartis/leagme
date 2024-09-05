// self.addEventListener('fetch', function(event) {
//   event.respondWith(
//     fetch(event.request).catch(function() {
//       // Return offline.html if the network request fails
//       return caches.match('/static/js/offline.html').then(function(response) {
//         return response || fetch('/static/js/offline.html');
//       });
//     })
//   );
// });




// self.addEventListener('install', function (event) {
//   console.log('Service worker installing.............');
//   console.log('network ok............');

//   event.waitUntil(
//     caches.open('v1').then(function (cache) {
//       return cache.addAll([
//         '/static/js/offline.html', // Uistite sa, že máte túto stránku v cache
//         // Môžete pridať ďalšie zdroje, ktoré chcete cacheovať
//       ]);
//     })
//   );

//   // alert('network ok');
//   // Tu môžete napríklad uložiť základné súbory do cache
// });

const CACHE_NAME = 'offline-cache';
const OFFLINE_URL = '/static/js/offline.html';

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll([
        OFFLINE_URL,
        // Tu môžete pridať ďalšie zdroje na kešovanie
      ]);
    })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    fetch(event.request).catch(function() {
      return caches.match(OFFLINE_URL);
    })
  );
});




const urlBase64ToUint8Array = base64String => {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

  const rawData = atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

const saveSubscription = async (subscription) => {
  const response = await fetch('/save-subscription', {
      method: 'post',
      headers: { 'Content-type': "application/json" },
      body: JSON.stringify(subscription)
  })

  return response.json()
}


//   self.addEventListener('install', function(event) {
//     console.log('Service worker installing...');
//     console.log('network ok');
  

//    // alert('network ok');
//     // Tu môžete napríklad uložiť základné súbory do cache
//   });

// self.addEventListener("activate", async (e) => {
//   e.waitUntil((async () => {
//     try {
//       // Získání veřejného klíče VAPID z backendu
//       const response = await fetch('/vapid-public-key');
//       const data = await response.json();
//       const vapidPublicKey = data.publicKey;

//       // Převod veřejného klíče do správného formátu
//       const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey);

//       // Odběr push notifikací
//       const subscription = await self.registration.pushManager.subscribe({
//         userVisibleOnly: true,
//         applicationServerKey: convertedVapidKey
//       });

//       // Uložení odběru na server
//       await saveSubscription(subscription);
//     } catch (error) {
//       console.error('Chyba při aktivaci:', error);
//     }
//   })());
// });


self.addEventListener('push', function(event) {
  const data = event.data.json();
   console.log("//////////////////////////"+data.data.totalUnread);

  event.waitUntil(
    (async function() {
      if ('setAppBadge' in navigator && data.data.totalUnread > 0) {
        await navigator.setAppBadge(data.data.totalUnread);
      } else {
        if ('clearAppBadge' in navigator) {
          await navigator.clearAppBadge();
        }
      }

      // Pridanie odkazu do notifikácie
      const notificationOptions = {
        body: data.notification.body,
        icon: data.notification.icon || '/static/img/icon.png',
        data: {
          url:'/',
          roomId: data.data.roomId,
          // url: data.notification.url // Pridajte URL odkaz, na ktorý chcete presmerovať
        }
      };
      await self.registration.showNotification(data.notification.title, notificationOptions);
    })()
  );
});

// Reakcia na kliknutie na notifikáciu
self.addEventListener('notificationclick', function(event) {
  event.notification.close(); // Zatvorte notifikáciu

  // Otvorte hlavnú stránku a pošlite POST request na nastavenie session pre miestnosť
  event.waitUntil(
    clients.matchAll({type: 'window'}).then(windowClients => {
      const client = windowClients.find(windowClient => {
        return windowClient.visibilityState === 'visible';
      });

      // Otvorte hlavnú stránku, ak už nie je otvorená
      if (client !== undefined) {
        client.navigate(event.notification.data.url).then(client => {
          // Tu môžete poslať správu klientovi, ak je to potrebné
        });
      } else {
        client.openWindow(event.notification.data.url);
      }

      // Tu môžete pridať logiku na odoslanie POST requestu na váš server
      // Toto je zložitejšie, pretože z Service Workeru nemôžete priamo poslať POST request
      // Môžete však poslať správu do klienta (napríklad otvorenej karty), ktorý potom môže poslať POST request.
    })
  );
});



