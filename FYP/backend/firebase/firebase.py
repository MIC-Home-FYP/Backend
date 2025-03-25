import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

class FirebaseMessenger:
    cred = credentials.Certificate("FYP/backend/firebase/service-account.json")
    firebaseApp = firebase_admin.initialize_app(cred)
    

    def sendToToken(self):
        REGISTRATION_TOKEN = 'enfFQu4GRRa_xaJGyYMFN1:APA91bEJMjCy1bF0Kfv3v4EhEUoA6G6kyNkPirKBZQOH-d1eMMztmQ0ScU6IzZuily8DNC8_-Zl0NG7yA5REggG4LwVks49-HrfWRAAsNWyC_8ALfwUdZiI' # TODO make secret

        message = messaging.Message(
            notification = messaging.Notification(
            title = "Take your meds",
            body = "Take tylenol at 06:00"
            ),
            token = REGISTRATION_TOKEN,
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

def __main__():
    messenger = FirebaseMessenger()
    messenger.sendToToken()

if __name__ == "__main__":
    __main__()