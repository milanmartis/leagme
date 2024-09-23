const checkPermission = () => {
    if (!('serviceWorker' in navigator)) {
        throw new Error("No support for service worker!")
    }

    if (!('Notification' in window)) {
        throw new Error("No support for notification API");
    }

    if (!('PushManager' in window)) {
        throw new Error("No support for Push API")
    }
}

const registerSW = async () => {
    const registration = await navigator.serviceWorker.register('/static/js/firebase-messaging-sw.js');
    return registration;
}

const requestNotificationPermission = async () => {
    const permission = await Notification.requestPermission();

    if (permission !== 'granted') {
        throw new Error("Notification permission not granted")
    }

}

const main = async () => {
    checkPermission()
    await requestNotificationPermission()
    await registerSW()
}

main()




function formatDate(dateString) {
    const messageDate = new Date(dateString);
    const now = new Date();

    const oneMinute = 60000;
    const oneDay = 24 * 60 * 60 * 1000;
    const oneWeek = 7 * 24 * 60 * 60 * 1000;

    const timeDifference = now - messageDate;

    if (timeDifference < oneMinute) {
        return "teraz";
    } else if (timeDifference < oneDay) {
        return messageDate.getHours().toString().padStart(2, '0') + ":" +
            messageDate.getMinutes().toString().padStart(2, '0');
    } else if (timeDifference < oneWeek) {
        const days = ["Nedeľa", "Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota"];
        return days[messageDate.getDay()] + " " +
            messageDate.getHours().toString().padStart(2, '0') + ":" +
            messageDate.getMinutes().toString().padStart(2, '0');
    } else {
        return messageDate.getDate().toString().padStart(2, '0') + ". " +
            (messageDate.getMonth() + 1).toString().padStart(2, '0') + ". " +
            messageDate.getFullYear();
    }
}



document.addEventListener("DOMContentLoaded", function () {



    // if ('serviceWorker' in navigator) {

    //     // var publicVapidKey = "{{ public_vapid_key }}";

    //     //  alert(publicVapidKey);

    //     navigator.serviceWorker.register('/static/js/service-worker.js')
    //         .then(function (registration) {
    //             console.log('Service Worker Registered!', registration);

    //             return registration.pushManager.subscribe({
    //                 userVisibleOnly: true,
    //                 applicationServerKey: vapid_public_key
    //             });
    //         })
    //         .then(function (subscription) {
    //             fetch('/save-subscription', {
    //                 method: 'POST',
    //                 headers: {
    //                     'Content-Type': 'application/json'
    //                 },
    //                 body: JSON.stringify(subscription)
    //             });
    //         });








    // }

    // Skontrolovať dostupnosť servera
    function checkServerStatus() {
        fetch('/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server response not OK');
                }
                console.log('Server is up and running');
            })
            .catch(error => {
                console.error('Server error or not reachable:', error);
                window.location.href = '/static/js/offline.html'; // Presmerovanie na offline stránku
            });
    }

    // Kontrola pri načítaní stránky
   // window.addEventListener('load', checkServerStatus);
});


function sendNotification(token, username, messageText) {
    fetch('/send-notification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            token: token, // Token získaný od klienta
            title: username, // Uživatelské jméno jako titulek notifikace
            body: messageText // Text zprávy jako obsah notifikace
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Notification sent:', data);
    })
    .catch(error => {
        console.error('Error sending notification:', error);
    });
}




function saveTokenToServer(userId, token) {
    // URL vašeho serveru, kde je endpoint /save-token
    const url = '/save-token';

    // Tělo požadavku
    const data = {
        user_id: userId,
        token: token
    };

    // Vytvoření požadavku
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}





// Initialize Firebase in your project
// firebase.initializeApp({
//     // Your Firebase config
// });

// // Get the messaging object
// const messaging = firebase.messaging();

// // Add event listener to your form
// document.getElementById('messageForm').addEventListener('submit', function(event) {
//     event.preventDefault();

//     // Get form values
//     const title = document.getElementById('messageTitle').value;
//     const body = document.getElementById('messageBody').value;

//     // Send a message to your server to trigger the notification
//     fetch('/send-notification', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//             token: 'your-subscribed-client-token', // Replace with the client's token
//             title: title,
//             body: body
//         })
//     })
//     .then(response => response.json())
//     .then(data => {
//         console.log('Notification sent:', data);
//     })
//     .catch(error => {
//         console.error('Error sending notification:', error);
//     });
// });
document.addEventListener("DOMContentLoaded", function () {
    const enableNotificationsButton = document.getElementById('enable-notifications');

    // Skontrolujte, či už bol povolený stav notifikácií
    if (Notification.permission === 'granted') {
        // Notifikácie sú už povolené, tlačidlo nemusí byť zobrazené
        if (enableNotificationsButton) {
            enableNotificationsButton.style.display = 'none';
        }
        console.log('Notifikácie sú už povolené.');
    } else if (Notification.permission === 'denied') {
        // Užívateľ už zamietol notifikácie, tlačidlo nemusí byť zobrazené
        if (enableNotificationsButton) {
            enableNotificationsButton.style.display = 'none';
        }
        console.log('Užívateľ zamietol notifikácie.');
    } else {
        // Notifikácie nie sú ani povolené ani zamietnuté, zobrazte tlačidlo
        if (enableNotificationsButton) {
            enableNotificationsButton.style.display = '';
            enableNotificationsButton.addEventListener('click', function() {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        // Užívateľ udelenie povolenia, tlačidlo sa skryje
                        enableNotificationsButton.style.display = 'none';
                        console.log('Notifikácie boli povolené.');

                        // Tu môžete zobraziť notifikáciu ako potvrdenie povolenia
                    } else {
                        // Ak bol stav zmenený na 'denied', tlačidlo môže byť tiež skryté
                        enableNotificationsButton.style.display = 'none';
                    }
                });
            });
        } else {
            console.log("'enable-notifications' element not found");
        }
    }
   

    
    window.addEventListener('online', function(e) {
    // Uživatel se vrátil online, můžete obnovit síťové operace
    console.log("you are online!");
    window.location.href = '/';

});

window.addEventListener('offline', function(e) {
    // Uživatel je offline, upozorněte ho a pozastavte síťové operace
    console.log("you are offline!");
    window.location.href = '/static/js/offline.html';
});


    // let startTouchY = 0;
    // let touchMoved = false;

    // document.addEventListener('touchstart', function(e) {
    //     startTouchY = e.touches[0].pageY;
    //     touchMoved = false;
    // }, {passive: true});

    // document.addEventListener('touchmove', function(e) {
    //     const touchY = e.touches[0].pageY;
    //     // Detekcia potiahnutia nadol
    //     if (touchY - startTouchY > 50) {
    //         touchMoved = true;
    //     }
    // }, {passive: true});

    // document.addEventListener('touchend', function(e) {
    //     if (touchMoved) {
    //         // Tu vykonajte akciu obnovenia
    //         window.location.reload();
    //     }
    // }, {passive: true});


/*

    let deferredPrompt;

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault(); // Zabrániť zobrazeniu natívneho výzvu
      deferredPrompt = e; // Uložiť udalosť pre neskoršie použitie
      $('#installModal').modal('show'); // Zobrazenie modálneho okna pomocou Bootstrap
    });
    



document.getElementById('installButton').addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt(); // Zobrazenie inštalačného výzvu
      const { outcome } = await deferredPrompt.userChoice; // Čakanie na rozhodnutie používateľa
  
      if (outcome === 'accepted') {
        console.log('Používateľ prijal inštalačný výzvu');
      } else {
        console.log('Používateľ odmietol inštalačný výzvu');
      }
  
      deferredPrompt = null;
      $('#installModal').modal('hide'); // Skrytie modálneho okna po rozhodnutí
    }
  });
*/
});





