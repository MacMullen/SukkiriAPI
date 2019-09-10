from google.cloud import firestore

from lib.classes import User

email = input("Admin email:")
username = input("Admin username:")
password = input("Admin password:")
first_name = input("Admin first name:")
last_name = input("Admin last name:")

new_user = User(email=email if 'email' in email else None,
                username=username,
                password=password,
                first_name=first_name if 'first_name' in first_name else None,
                last_name=last_name if 'last_name' in last_name else None,
                role="admin")

db = firestore.Client()
db.collection('users').document(new_user.public_id).set(new_user.to_dict())

print("User created successfully!")
