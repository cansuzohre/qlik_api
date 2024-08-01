from qlik_connect import *

# Initials
QLIK_SENSE_SERVER_DOMAIN = input("Enter Qlik Sense Server Domain without 'https://' : ")
USER_DIRECTORY = input("Enter User Directory (for instance, ASLROMA): ")
USER_ID = input("Enter User ID: ")
APP_ID = input("Enter App ID for the dummy call: ")

# Activate library
qlik = QlikConnect(domain=QLIK_SENSE_SERVER_DOMAIN, user_directory=USER_DIRECTORY, user_id=USER_ID, app_id=APP_ID)

# Connect to the Qlik Sense Server
qlik.connect()

# App list
doc_list = qlik.get_doclist()
print("Available documents:")
for i, doc in enumerate(doc_list):
    print(f"{i + 1}: {doc['name']} (ID: {doc['id']})")

# App selection
selection = int(input("Select a document number to open: ")) - 1

if 0 <= selection < len(doc_list):
    selected_doc_id = doc_list[selection]['id']
    # Open the doc
    qlik.open_document(selected_doc_id)
    app_req_handle = result_json['result']['qReturn']['qHandle']
    # Export data

else:
    print("Invalid selection.")

# Close connection
qlik.close_connection()
