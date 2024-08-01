import websocket
import ssl
import json
import pandas as pd
from io import BytesIO
import time


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

        # API URL
        self.engine_api_url = f"wss://{self.domain}/{self.proxy_prefix}/app/{self.app_id}/"

        # SSL CONTEXT
        self.ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(certfile=self.cert_path, keyfile=self.key_path)

        # MESSAGE TEMPLATES
        self.msg_dummy_first = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "QTProduct",
            "handle": self.qlik_global_context,
            "params": []
        }
        self.msg_get_doclist = {
            "handle": self.qlik_global_context,
            "method": "GetDocList",
            "params": [],
            "outKey": -1,
            "id": 1
        }

        self.msg_open_doc = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "OpenDoc",
            "handle": self.qlik_global_context,
            "params": [
                None  # Document ID will be set dynamically -- if it was specific, then: self.app_id
            ]
        }
        self.msg_evaluate_expression = {
            "handle": 1,
            "method": "EvaluateEx",
            "params": [
                None  # measure will be defined dynamically
            ],
            "id": 3,
            "outKey": -1
        }

        self.msg_get_field = {"jsonrpc": "2.0",
                              "id": 4,
                              "method": "GetField",
                              "handle": 1,
                              "params": [
                                  None  # field will be defined dynamically
                              ]}

        self.msg_select_field = {"jsonrpc": "2.0",
                                 "id": 5,
                                 "method": "Select",
                                 "handle": 2,
                                 "params": [
                                     None  # field value will be defined dynamically
                                 ]}

        self.msg_get_table_data = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "GetTableData",
            "handle": None,
            "params": {
                "qOffset": 0,
                "qCount": 10000  # Adjust as needed for the number of rows you want
            }
        }
        self.msg_export_data = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "ExportData",
            "handle": 1,
            "params": [
                "CSV_T",  # File type, "CSV_C" for CSV with commas, OOXML for Excel, CSV_T for tabs
                "/qHyperCubeDef",  # Path to the object's data definition
                "DataExport.csv"  # File name (optional, not used in some setups)
            ]
        }

        self.get_tables_and_keys_req_template = {
            "jsonrpc": "2.0",
            "id": 10,
            "handle": None,  # To be set dynamically
            "method": "GetTablesAndKeys",
            "params": {
                "qWindowSize": {"qcx": 1, "qcy": 1},
                "qNullSize": {"qcx": 1, "qcy": 1},
                "qCellHeight": 1,
                "qSyntheticMode": True,
                "qIncludeSysVars": False,
                "qIncludeProfiling": False
            }
        }

        self.get_table_data_req_template = {
            "jsonrpc": "2.0",
            "id": 11,
            "handle": None,  # To be set dynamically
            "method": "GetTableData",
            "params": {
                "qOffset": 0,
                "qRows": 1000,
                "qSyntheticMode": True,
                "qTableName": None  # To be set dynamically
            }
        }

        self.msg_create_session_object = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "CreateSessionObject",
            "handle": 1,
            "params": [
                {
                    "qInfo": {
                        "qId": "",
                        "qType": "Chart"
                    },
                    "qHyperCubeDef": {
                        "qStateName": "$",
                        "qDimensions": [
                            {
                                "qLibraryId": "",
                                "qNullSuppression": False,
                                "qDef": {
                                    "qGrouping": "N",
                                    "qFieldDefs": [
                                        None
                                    ],
                                    "qFieldLabels": [
                                        None
                                    ]
                                }
                            }
                        ],
                        "qMeasures": [
                            {
                                "qLibraryId": "",
                                "qSortBy": {
                                    "qSortByState": 0,
                                    "qSortByFrequency": 0,
                                    "qSortByNumeric": 0,
                                    "qSortByAscii": 0,
                                    "qSortByLoadOrder": 1,
                                    "qSortByExpression": 0,
                                    "qExpression": {
                                        "qv": ""
                                    }
                                },
                                "qDef": {
                                    "qLabel": "",
                                    "qDescription": "",
                                    "qTags": [
                                        "tags"
                                    ],
                                    "qGrouping": "N",
                                    "qDef": None
                                }
                            },
                            {
                                "qLibraryId": "",
                                "qSortBy": {
                                    "qSortByState": 0,
                                    "qSortByFrequency": 0,
                                    "qSortByNumeric": 0,
                                    "qSortByAscii": 0,
                                    "qSortByLoadOrder": 1,
                                    "qSortByExpression": 0,
                                    "qExpression": {
                                        "qv": ""
                                    }
                                },
                                "qDef": {
                                    "qLabel": "",
                                    "qDescription": "",
                                    "qTags": [
                                        "tags"
                                    ],
                                    "qGrouping": "N",
                                    "qDef": ""
                                }
                            }
                        ],
                        "qInitialDataFetch": [
                            {
                                "qTop": 0,
                                "qLeft": 0,
                                "qHeight": 3,
                                "qWidth": 1
                            },
                            {
                                "qTop": 0,
                                "qLeft": 0,
                                "qHeight": 0,
                                "qWidth": 0
                            },
                            {
                                "qTop": 0,
                                "qLeft": 0,
                                "qHeight": 0,
                                "qWidth": 0
                            }
                        ]
                    }
                }
            ]
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

    def get_doclist(self):
        # self.connect()
        self.ws.send(json.dumps(self.msg_get_doclist))
        result = self.ws.recv()

        if isinstance(result, bytes):
            result = result.decode('utf-8')  # Decode bytes to string

        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return []

        doclist = []

        while parsed_result:

            if parsed_result.get('id') == self.msg_get_doclist['id']:
                docs = parsed_result.get('result', {}).get('qDocList', [])
                for doc in docs:
                    doclist.append({
                        'id': doc.get('qDocId', ''),
                        'name': doc.get('qDocName', '')
                    })
                break

            # Continue receiving messages if needed
            result = self.ws.recv()
            if isinstance(result, bytes):
                result = result.decode('utf-8')
            try:
                parsed_result = json.loads(result)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                break

        return doclist

    def select_and_open_document(self):
        doclist = self.get_doclist()
        if not doclist:
            print("No documents found.")
            return

        print("Available documents:")
        for i, doc in enumerate(doclist):
            print(f"{i + 1}: {doc['name']}")

        selection = int(input("Select a document number to open: ")) - 1

        if 0 <= selection < len(doclist):
            selected_doc = doclist[selection]
            self.open_document(selected_doc['id'])
        else:
            print("Invalid selection.")

    def open_document(self, doc_id):
        print(f"\nOpening the doc: {doc_id}\n")
        self.msg_open_doc['params'][0] = doc_id
        self.ws.send(json.dumps(self.msg_open_doc))
        open_doc_id = self.msg_open_doc['id']

        start_time = time.time()
        timeout = 10  # seconds
        doc_handle = None

        while time.time() - start_time < timeout:
            try:
                result = self.ws.recv()
                if isinstance(result, bytes):
                    result = result.decode('utf-8')
                parsed_result = json.loads(result)

                print(f"Received result: {parsed_result}")

                if parsed_result.get('id') == open_doc_id:
                    doc_handle = parsed_result.get('result', {}).get('qReturn', {}).get('qHandle', None)
                    if doc_handle:
                        print(f"Received handle {doc_handle} for doc {doc_id}")
                        break

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")

        if not doc_handle:
            print(f"Failed to get document handle for doc {doc_id} within the timeout period.")
        else:
            self.msg_evaluate_expression['handle'] = doc_handle

    def evaluate_expression(self, formula):
        print("simple call\n")
        self.msg_evaluate_expression['params'][0] = formula
        self.ws.send(json.dumps(self.msg_evaluate_expression))
        result = self.ws.recv()
        print(json.loads(result))

    def get_field(self, field):
        self.msg_get_field['params'][0] = field
        self.ws.send(json.dumps(self.msg_get_field))
        result = self.ws.recv()
        print(json.loads(result))

    def select_field(self, field_value):
        self.msg_select_field['params'][0] = field_value
        self.ws.send(json.dumps(self.msg_select_field))
        result = self.ws.recv()
        print(json.loads(result))

    def get_object_handle(self, object_id):

        get_object_msg = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "GetObject",
            "handle": self.qlik_global_context,
            "params": [
                object_id
            ]
        }

        self.ws.send(json.dumps(get_object_msg))
        result = json.loads(self.ws.recv())
        print("GetObject result:", result)

        if 'result' in result and 'qReturn' in result['result']:
            return result['result']['qReturn']['qHandle']
        else:
            print("Failed to retrieve object handle.")
            return None

    def get_tables_and_keys(self):
        req = self.get_tables_and_keys_req_template.copy()
        req['handle'] = self.qlik_global_context

        self.ws.send(json.dumps(req))
        result = json.loads(self.ws.recv())
        print("GetTablesAndKeys Response:", result)

        if 'error' in result:
            raise ValueError(f"Error in GetTablesAndKeys response: {result['error']['message']}")

        return result

    def get_table_data(self, table_name):
        req = self.get_table_data_req_template.copy()
        req['handle'] = self.qlik_global_context
        req['params']['qTableName'] = table_name

        self.ws.send(json.dumps(req))
        result = json.loads(self.ws.recv())
        print("GetTableData Response:", result)

        if 'error' in result:
            raise ValueError(f"Error in GetTableData response: {result['error']['message']}")

        return result

    def create_session_obj(self, field_name, measure_expr):
        self.msg_create_session_object["params"][0]["qHyperCubeDef"]["qDimensions"][0]["qDef"]["qFieldDefs"] = [field_name]
        self.msg_create_session_object["params"][0]["qHyperCubeDef"]["qDimensions"][0]["qDef"]["qFieldLabels"] = [field_name]
        self.msg_create_session_object["params"][0]["qHyperCubeDef"]["qMeasures"][0]["qDef"]["qDef"] = measure_expr

        self.ws.send(json.dumps(self.msg_create_session_object))
        result = self.ws.recv()
        print(json.loads(result))

    def export_chart_data(self, app_req_handle):
        # -------------------------------------------------------------------------------------------------------
        # Exports the data of any generic object to an Excel file or an open XML file.
        # If the object contains excluded values, those excluded values are not exported.
        # This API has limited functionality and will not support CSV export from all types of objects.
        # Consider using Excel export instead. Treemap and bar chart are not supported.
        # -------------------------------------------------------------------------------------------------------
        layout_json = self.get_layout(app_req_handle)
        list_of_charts = layout_json['result']['qLayout']['qAppObjectList']['qItems'][0]['qData']['cells']
        id = 6

        for chart in list_of_charts:
            obj_req = {
                "jsonrpc": "2.0",
                "method": "GetObject",
                "handle": app_req_handle,
                "params": [chart["name"]],
                "outKey": -1,
                "id": id
            }

            self.ws.send(json.dumps(obj_req))
            result = json.loads(self.ws.recv())
            obj_req_handle = result['result']['qReturn']['qHandle']

            export_req = {
                "jsonrpc": "2.0",
                "method": "ExportData",
                "handle": obj_req_handle,
                "params": ["OOXML"],
                "outKey": -1,
                "id": id + 1
            }

            self.ws.send(json.dumps(export_req))
            result = json.loads(self.ws.recv())

            download_url = result["result"]["qUrl"]
            r = requests.get(download_url, allow_redirects=True)
            with open(f'export_python_{chart["name"]}.xlsx', 'wb') as f:
                f.write(r.content)

            id += 1

    def close_connection(self):
        if self.ws:
            self.ws.close()
