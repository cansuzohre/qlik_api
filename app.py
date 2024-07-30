from qlik_connect import *

# Initials
QLIK_SENSE_SERVER_DOMAIN = input("Enter Qlik Sense Server Domain without 'https://' : ")
USER_DIRECTORY = input("Enter User Directory (for instance, ASLROMAB): ")
USER_ID = input("Enter User ID: ")
APP_ID = input("Enter App ID: ")

# Activate library
qlik = QlikConnect(domain=QLIK_SENSE_SERVER_DOMAIN, user_directory=USER_DIRECTORY, user_id=USER_ID, app_id=APP_ID)

# Connect to server
qlik.connect()

# Open the document
qlik.open_document()

# Evaluate an expression
qlik.evaluate_expression()

# Export chart data and get DataFrame
OBJECT_ID = input("Enter Object ID: ")
df_qlik = qlik.export_chart_data(OBJECT_ID)
print(df_qlik.head())

# Close connection
qlik.close_connection()
