import websocket
import ssl
import json

QLIK_GOBLAL_CONTEXT = -1  # entry point for base functionality like "OpenDoc"

# Initials
QLIK_SENSE_SERVER_DOMAIN = input("Enter Qlik Sense Server Domain without 'https://' : ")
USER_DIRECTORY = input("Enter User Directory (for instance, ASLROMAB): ")
USER_ID = input("Enter User ID: ")
APP_ID = input("Enter App ID: ")
PROXY_PREFIX = 'py_api'

ENGINE_API_URL = f"wss://{QLIK_SENSE_SERVER_DOMAIN}/{PROXY_PREFIX}/app/{APP_ID}/"

# Use pem format.
cert_path = './certificates/client.pem'
key_path = './certificates/client_key.pem'

# Create a custom ssl context
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=cert_path, keyfile=key_path)

header_user = {
    'header_user': f'{USER_DIRECTORY}\\{USER_ID}',
    # you've to declare 'header_user' literal in the virtual-proxy setting called "header authentication header name"
}

ws = websocket.create_connection(ENGINE_API_URL,
                                 sslopt={"cert_reqs": ssl.CERT_NONE, "ssl_context": ssl_context},
                                 header=header_user)

msg_dummy_first = {
    "jsonrpc": "2.0",
    "id": 0,
    "method": "QTProduct",
    "handle": QLIK_GOBLAL_CONTEXT,
    "params": []
}

msg_open_doc = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "OpenDoc",
    "handle": QLIK_GOBLAL_CONTEXT,
    "params": [
        APP_ID
    ]
}

msg_evaluate_expression = {"handle": 1,
                           "method": "EvaluateEx",
                           "params": {"qExpression": "=127"},
                           "id": 2,
                           "outKey": -1}

print('dummy call \n'
      '(this is necessary since, for some authentication methods, '
      'the "OnAuthenticationInformation" message will be sent by the server only after a valid message '
      'has been received from the client. )\n')
ws.send(json.dumps(msg_dummy_first))

result = json.loads(ws.recv())
print(result)
print()

if 'params' in result and 'mustAuthenticate' in result['params']:
    if not result['params']['mustAuthenticate']:
        print("correctly authenticated")
    else:
        print("authentication error:")
else:
    print("OMG! no authentication info!!!")

print("\nopening the doc:", APP_ID, "\n")
ws.send(json.dumps(msg_open_doc))
open_doc_id = msg_open_doc['id']

result = json.loads(ws.recv())
print(result, "\n")

i = 1
doc_handle = False
while result and not doc_handle:
    result = ws.recv()
    parsed_result = json.loads(result) if result is not None and result != "" else "None"
    print(f"result JSON {i}\n", parsed_result)
    i += 1

    if parsed_result is not None and parsed_result.get('id', None) == open_doc_id:
        doc_handle = parsed_result.get('result', {}).get('qReturn', {}).get('qHandle', False)

print(f"\nreceived handle {doc_handle} for app {APP_ID}\n")
msg_evaluate_expression['handle'] = doc_handle

print("simple call\n")
ws.send(json.dumps(msg_evaluate_expression))

result = ws.recv()
print(json.loads(result))
print()

ws.close()
