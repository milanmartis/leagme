import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging.js";
// VAPID public key
const publicVapidKey = vapidPublicKey;
//alert(publicVapidKey);

// Function to detect iOS devices
function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
}

// Function to check if notifications are supported
function checkNotificationSupport() {
    if (!("Notification" in window)) {
        console.error("This browser does not support notifications.");
        return false;
    }
    return true;
}

// Request Notification Permission
async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        console.log("Notification permission status:", permission);
        return permission === 'granted';
    } catch (error) {
        console.error('Error while requesting notification permission:', error);
        return false;
    }
}

// Function to register service worker and request FCM token
async function subscribeToPushNotifications() {
    if (!checkNotificationSupport()) {
        console.error('Browser does not support notifications.');
        return;
    }

    if ('serviceWorker' in navigator) {
        try {
            // Register service worker for Web Push
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker registered successfully.');

            // iOS detection and Firebase Cloud Messaging for iOS
            if (isIOS()) {
                console.log('iOS detected. Using Firebase for push notifications.');

                const permissionGranted = await requestNotificationPermission();
                if (!permissionGranted) {
                    console.error('Notification permission denied on iOS.');
                    return;
                }
            
                // Fetch and initialize Firebase
                const response = await fetch('/get-firebase-config');
                const firebaseConfig = await response.json();
                
                const app = initializeApp(firebaseConfig);
                const messaging = getMessaging(app);

                const deviceInfo = getDeviceInfo();
            
                // Get token
                getToken(messaging, { vapidKey: publicVapidKey, serviceWorkerRegistration: registration })
                    .then((currentToken) => {
                        if (currentToken) {
                            console.log('FCM token:', currentToken);
                           
                            fetch('/subscribe', {
                                method: 'POST',
                                body: JSON.stringify({ 
                                    token: currentToken,
                                    deviceType: deviceInfo.deviceType,
                                    operatingSystem: deviceInfo.operatingSystem,
                                    browserName: deviceInfo.browserName
                                }),
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken
                                }
                            });

                        } else {
                            console.log('No FCM token available.');
                        }
                    })
                    .catch((err) => {
                        console.error('An error occurred while retrieving FCM token:', err);
                    });

            } else {
                // Handle Web Push for other platforms (non-iOS)
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    console.error('Push notifications permission not granted.');
                    return;
                }

                const subscription = await registration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(publicVapidKey)
                });

                console.log('Subscription data:', subscription);
                const deviceInfo = getDeviceInfo();

                // Send subscription data to backend
               // alert(subscription.endpoint);
                const response = await fetch('/subscribe', {
                    method: 'POST',
                    body: JSON.stringify({ 
                        subscription: subscription,
                        deviceType: deviceInfo.deviceType,
                        operatingSystem: deviceInfo.operatingSystem,
                        browserName: deviceInfo.browserName
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });

                if (!response.ok) {
                    console.error('Failed to send subscription to server.');
                } else {
                    console.log('Successfully subscribed to push notifications.');
                }
            }
        } catch (error) {
            console.error('Push notifications subscription failed:', error);
        }
    } else {
        console.error('Service Worker not supported in this browser.');
    }
}

// Function to convert VAPID key to Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }

    return outputArray;
}




async function unsubscribeFromPushNotifications() {
    // alert('unsub');

    // const current_user =  current_user;
    
    try {
        // const serviceWorkerRegistration = await navigator.serviceWorker.ready;
        // const subscription = await serviceWorkerRegistration.pushManager.getSubscription();
  
        // if (subscription) {
        //     await subscription.unsubscribe();
        //     console.log('User is unsubscribed.');
  
            // Odošleme požiadavku na backend na vymazanie subscription z databázy
            const deviceInfo = getDeviceInfo();
            fetch('/unsubscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken  // Ak používaš CSRF ochranu
                },
                body: JSON.stringify({ 
                    user_id:  current_user,
                    device_type: deviceInfo.deviceType,
                    operating_system: deviceInfo.operatingSystem,
                    browser_name: deviceInfo.browserName
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Unsubscribed on server:', data);
            })
            .catch(error => {
                console.error('Error unsubscribing on server:', error);
            });

    } catch (error) {
        console.error('Failed to unsubscribe the user:', error);
    }
  }
  
  
  document.getElementById('enableNotificationsToggle').addEventListener('change', async (event) => {
    const notifTextSwitch = document.getElementById('notif-text-switch');
    const notifTextSwitch2 = document.getElementById('notif-text-switch2');
    
    // Nastav opacity na zníženie viditeľnosti pri spracovaní
   // notifTextSwitch.style.opacity = '0.3';
    
    if (event.target.checked) {
      try {
        await subscribeToPushNotifications();  // Funkcia na prihlásenie k odberu
       // notifTextSwitch.textContent = 'Notifications enabled';
        notifTextSwitch.style.opacity = '0.4';
        notifTextSwitch2.style.opacity = '0.4';

      } catch (error) {
        console.error('Error subscribing to notifications:', error);
      }
    } else {
      try {
        await unsubscribeFromPushNotifications();  // Funkcia na odhlásenie z odberu
        notifTextSwitch.style.opacity = '1';
        notifTextSwitch2.style.opacity = '1';

      } catch (error) {
        console.error('Error unsubscribing from notifications:', error);
      }
    }
  
    // Po spracovaní obnov opacity na plnú viditeľnosť
   // notifTextSwitch.style.opacity = '1';
  });
  
  
  // Funkcia na kontrolu stavu predplatného
  async function checkSubscriptionStatus() {
    const notifTextSwitch = document.getElementById('notif-text-switch');
    const notifTextSwitch2 = document.getElementById('notif-text-switch2');

    try {
        // const serviceWorkerRegistration = await navigator.serviceWorker.ready;
        // const subscription = await serviceWorkerRegistration.pushManager.getSubscription();
        // alert(subscription);
  
        // if (subscription) {
            // Načítanie stavu predplatného z backendu
          //  alert('zle');
            const deviceInfo = getDeviceInfo();
            const response = await fetch(`/check-subscription?device_type=${deviceInfo.deviceType}&operating_system=${deviceInfo.operatingSystem}&browser_name=${deviceInfo.browserName}&user_id=${current_user}`);
            const data = await response.json();
            // alert(data.subscribed);
  
            if (data.subscribed) {
                // Ak je používateľ už predplatený, nastav tlačidlo na zapnuté

                document.getElementById('enableNotificationsToggle').checked = true;
                notifTextSwitch.style.opacity = '0.4';
                notifTextSwitch2.style.opacity = '0.4';
            } else {
                document.getElementById('enableNotificationsToggle').checked = false;
                notifTextSwitch.style.opacity = '1';
                notifTextSwitch2.style.opacity = '1';
                // Ak nie je predplatený, nastav tlačidlo na vypnuté
            }
        // } else {
            // document.getElementById('enableNotificationsToggle').checked = false;
        // }
    } catch (error) {
        console.error('Error checking subscription status:', error);
    }
  }
  
  // Zavolaj funkciu po načítaní stránky, aby sa načítal stav tlačidla
  window.addEventListener('load', checkSubscriptionStatus);

  // Attach the event listener to a button
document.getElementById('enableNotificationsButton').addEventListener('click', async () => {
    const permission = await Notification.requestPermission();
    if (permission === 'granted') {
        console.log('Permission granted.');
        await subscribeToPushNotifications();
    } else {
        console.log('Push notifications not granted.');
    }
});


function getDeviceInfo() {
    const userAgent = navigator.userAgent;

    // Detekcia zariadenia
    const isMobile = /Mobi|Android/i.test(userAgent);
    const deviceType = isMobile ? 'Mobile' : 'Desktop';

    // Detekcia operačného systému
    let operatingSystem = 'Unknown OS';
    if (/Windows/i.test(userAgent)) {
        operatingSystem = 'Windows';
    } else if (/Mac/i.test(userAgent)) {
        operatingSystem = 'MacOS';
    } else if (/Android/i.test(userAgent)) {
        operatingSystem = 'Android';
    } else if (/iPhone|iPad|iPod/i.test(userAgent)) {
        operatingSystem = 'iOS';
    } else if (/Linux/i.test(userAgent)) {
        operatingSystem = 'Linux';
    }

    // Detekcia prehliadača
    let browserName = 'Unknown Browser';
    if (/Chrome/i.test(userAgent)) {
        browserName = 'Chrome';
    } else if (/Firefox/i.test(userAgent)) {
        browserName = 'Firefox';
    } else if (/Safari/i.test(userAgent) && !/Chrome/i.test(userAgent)) {
        browserName = 'Safari';
    } else if (/Edge/i.test(userAgent)) {
        browserName = 'Edge';
    } else if (/Opera|OPR/i.test(userAgent)) {
        browserName = 'Opera';
    }

    return {
        deviceType,
        operatingSystem,
        browserName
    };
}


// Listener na zachytenie správ zo Service Workera
navigator.serviceWorker.addEventListener('message', event => {
    if (event.data === 'reset-badge') {
        console.log('Správa na resetovanie odznaku prijatá.');

        // Volanie backendu alebo iného mechanizmu na resetovanie stavu odznaku v IndexedDB
        resetUnreadCount();
    }
});

// Funkcia na resetovanie počtu neprečítaných správ v IndexedDB
async function resetUnreadCount() {
    const db = await openDatabase();
    const tx = db.transaction('notifications', 'readwrite');
    const store = tx.objectStore('notifications');
    store.put({ id: 1, count: 0 });
    await tx.complete;

    // Zresetuj aj App Badge
    if ('clearAppBadge' in navigator) {
        try {
            await navigator.clearAppBadge();
            console.log('Odznak App Badge bol úspešne resetovaný.');
        } catch (error) {
            console.error('Chyba pri resetovaní odznaku:', error);
        }
    }
}


