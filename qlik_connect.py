import websocket
import ssl
import json
import pandas as pd
from io import BytesIO


class QlikConnect:
    def __init__(self, domain, user_directory, user_id, app_id, cert_path='./certificates/client.pem',
                 key_path='./certificates/client_key.pem', proxy_prefix='py_api'):
        self.domain = domain
        self.user_directory = user_directory
        self.user_id = user_id
        self.app_id = app_id
        self.cert_path = cert_path
        self.key_path = key_path
        self.proxy_prefix = proxy_prefix
        self.ws = None
        self.qlik_global_context = -1  # entry point for base functionality like "OpenDoc"

        # Construct the API URL
        self.engine_api_url = f"wss://{self.domain}/{self.proxy_prefix}/app/{self.app_id}/"

        # Create a custom SSL context
        self.ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(certfile=self.cert_path, keyfile=self.key_path)

        # Define message templates
        self.msg_dummy_first = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "QTProduct",
            "handle": self.qlik_global_context,
            "params": []
        }
        self.msg_open_doc = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "OpenDoc",
            "handle": self.qlik_global_context,
            "params": [
                self.app_id
            ]
        }
        self.msg_evaluate_expression = {
            "handle": 1,
            "method": "EvaluateEx",
            "params": {"qExpression": "=127"},
            "id": 2,
            "outKey": -1
        }
        self.msg_get_object_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "GetTableData",
            "handle": None,
            "params": {
                "qOffset": 0,
                "qCount": 10000  # Adjust as needed for the number of rows you want
            }
        }
        self.msg_export_data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "ExportData",
            "handle": None,
            "params": {
                "qFileType": "OOXML",  # Change to "CSV_C" or "CSV_T" if exporting as CSV, but EXCEL is recommended
                "qPath": "/qHyperCubeDef",  # Use appropriate path if exporting CSV
                "qFileName": "",  # Optional: Name for the exported file (not used in SaaS)
                "qExportState": "A"  # "A" for all values, "P" for possible values
            }
        }

    def connect(self):
        header_user = {
            'header_user': f'{self.user_directory}\\{self.user_id}',
            # Define 'header_user' literal in the virtual-proxy setting called "header authentication header name"
        }
        self.ws = websocket.create_connection(self.engine_api_url,
                                              sslopt={"cert_reqs": ssl.CERT_NONE, "ssl_context": self.ssl_context},
                                              header=header_user)
        self._authenticate()

    def _authenticate(self):
        print('dummy call: ')
        # -------------------------------------------------------------------------------------------------
        # NOTE:
        # This is necessary since, for some authentication methods the "OnAuthenticationInformation" message
        # will be sent by the server only after a valid message has been received from the client.
        # -------------------------------------------------------------------------------------------------
        self.ws.send(json.dumps(self.msg_dummy_first))
        result = json.loads(self.ws.recv())
        print(result)
        print()

        if 'params' in result and 'mustAuthenticate' in result['params']:
            if not result['params']['mustAuthenticate']:
                print("CORRECTLY AUTHENTICATED")
            else:
                print("AUTHENTICATION ERROR: ")
        else:
            print("OMG! no authentication info!!!")

    def open_document(self):
        print("\nopening the doc:", self.app_id, "\n")
        self.ws.send(json.dumps(self.msg_open_doc))
        open_doc_id = self.msg_open_doc['id']

        result = json.loads(self.ws.recv())
        print(result, "\n")

        i = 1
        doc_handle = False
        while result and not doc_handle:
            result = self.ws.recv()
            parsed_result = json.loads(result) if result is not None and result != "" else "None"
            print(f"result JSON {i}\n", parsed_result)
            i += 1

            if parsed_result is not None and parsed_result.get('id', None) == open_doc_id:
                doc_handle = parsed_result.get('result', {}).get('qReturn', {}).get('qHandle', False)

        print(f"\nreceived handle {doc_handle} for app {self.app_id}\n")
        self.msg_evaluate_expression['handle'] = doc_handle

    def evaluate_expression(self):
        print("simple call\n")
        self.ws.send(json.dumps(self.msg_evaluate_expression))
        result = self.ws.recv()
        print(json.loads(result))
        print()

    def export_chart_data(self, object_id):
        # Exports the data of any generic object to an Excel file or an open XML file.
        # If the object contains excluded values, those excluded values are not exported.
        # This API has limited functionality and will not support CSV export from all types of objects.
        # Consider using Excel export instead. Treemap and bar chart are not supported.

        self.msg_export_data['params']['qPath'] = f"/{object_id}"  # Update path with the object ID if necessary

        self.ws.send(json.dumps(self.msg_export_data))
        result = json.loads(self.ws.recv())
        print("ExportData result:", result)

        # Handle response
        if 'result' in result and 'qUrl' in result['result']:
            file_url = result['result']['qUrl']
            print(f"Data exported to: {file_url}")

            # Download the file
            response = requests.get(file_url, verify=False)  # Disable SSL verification if needed
            if response.status_code == 200:
                # Load data into DataFrame
                df = pd.read_excel(BytesIO(response.content))
                return df
            else:
                print(f"Failed to download the file. HTTP status code: {response.status_code}")
                return None
        else:
            print("Failed to export data.")
            return None

    def close_connection(self):
        if self.ws:
            self.ws.close()
