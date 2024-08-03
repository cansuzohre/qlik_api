# Qlik Sense Python API

This project establishes a secure connection between Qlik Sense and Python, enabling communication via the Qlik Sense Engine API. It allows you to fetch and interact with data from specified pages (such as tables and charts) in the form of hypercubes, using Python to work with Qlik Sense applications and data.

## Getting Started

To get started, ensure you have the following prerequisites:

1. **Qlik Sense Environment Access**:
   - You need API access to your Qlik Sense environment. (Refer to the [Configuration](#configuration) section for details on creating certificates and a virtual proxy to establish an API connection for your user.)
   - Ensure you have access to the Qlik Sense Hub with a user ID that has Root Admin permissions.

2. **Python Installation**:
   - Python version 3.10 must be installed on your machine.

## Documentations (must read):

1. **"Qlik Sense: call Qlik Sense Engine API with Python" by Damien Villaret**  
   - [Call Qlik Sense Engine API with Python](https://community.qlik.com/t5/Official-Support-Articles/Qlik-Sense-call-Qlik-Sense-Engine-API-with-Python/ta-p/1716089)

2. **"Let's Dissect the Qlik Engine API" by Øystein Kolsrud:**
   - [Part 1: RPC Basics](https://community.qlik.com/t5/Qlik-Design-Blog/Let-s-Dissect-the-Qlik-Engine-API-Part-1-RPC-Basics/ba-p/1734116)
   - [Part 2: Handles](https://community.qlik.com/t5/Qlik-Design-Blog/Let-s-Dissect-the-Qlik-Engine-API-Part-2-Handles/ba-p/1737186)
   - [Part 3: Generic Objects](https://community.qlik.com/t5/Qlik-Design-Blog/Let-s-Dissect-the-Qlik-Engine-API-Part-3-Generic-Objects/ba-p/1761962)
   - [Part 4: Hypercubes](https://community.qlik.com/t5/Qlik-Design-Blog/Let-s-Dissect-the-Qlik-Engine-API-Part-4-Hypercubes/ba-p/1778450)
   - [Part 5: Multiple-Hypercube-Dimensions](https://community.qlik.com/t5/Design/Dissecting-the-Engine-API-Part-5-Multiple-Hypercube-Dimensions/ba-p/1841618)

## Installation

1. Clone the repository from Bitbucket to your local machine.
2. Create a virtual environment for your python program. 
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### 1. Create and Export Certificates

- Access the **Certificates** section in Qlik Sense QMC.

- Create a new certificate with the following settings:
  - **Machine Name**: Enter your local machine's name (Check via System Information on your computer).
  - **Certificate Password**: Leave this field empty; a password is not necessary.
  - **Include Secret Key**: Ensure this option is ticked.
  - **Export File Format**: Select "Platform independent PEM-format".

### 2. Register Certificates on Local Machine and Qlik Sense Server

After exporting the certificates, you need to register them on both your local machine and the Qlik Sense server:

- **Open the Microsoft Management Console (MMC) as an Administrator**:
   - Press `Win + R`, type `mmc`, and press Enter.

- **Add the Certificates Snap-in for the Local Computer**:
   - Go to "File" > "Add/Remove Snap-in".
   - Select "Certificates" and click "Add".
   - Choose "Computer account", then "Local computer".

- **Import Certificates**:
   - Navigate to `Trusted Root Certification Authorities`.
   - Right-click, select "All Tasks" > "Import", and import the `root.pem`, `client.pem`, and `client_key.pem` files.
   - If prompted with a warning message, select "Yes" to trust the certificates.

- **Import Personal Certificates**:
   - Navigate to `Personal`.
   - Right-click, select "All Tasks" > "Import", and import the `client.pem` file.

### 3. Create and Activate Windows Certificates

- **Create Windows Certificate**:
   - In Qlik Sense QMC, create a new certificate with the following setting:
   - **Export File Format**: Select "Windows".

- **Activate Certificates on Both Machines**:
   - Simply run the exported certificate files by double-clicking them.
   - Always select "Local Machine" during the installation process.

### 3. Create a Virtual Proxy on QMC server for the secure connection

- Refer to QMC, Virtual Proxies
- Click 'Create New'

  - **PROPERTIES**:
    - **Description**: Create a desired name
    - **Prefix**: py_api
    - **Session Inactivity Timeout (minutes)**: 30
    - **Session Cookie Header Name**: X-Qlik-Session-Api
    - **Anonymous Access Mode**: No anonymous user
    - **Authentication Method**: Header authentication dynamic user directory
    - **Header Authentication Header Name**: header_user
    - **Header Authentication Dynamic User Directory**: $ud\\$id
    - **Add New Server Node**: Add the central node to this virtual proxy
    - **Has Secure Attribute (https)**: Select
    - **SameSite Attribute (https)**: Lax
    - **Has Secure Attribute (http)**: NOT select
    - **SameSite Attribute (http)**: None
    - **Host Allow List**: Add your IP address; if connected via VPN, add VPN IP

  - **ASSOCIATED ITEMS**:
    - Click 'Link' and link it to the Central node.
  
### 5. Ensure your Python environment is secure and the connection is configured correctly

- Inside your Python application, correctly reference the certificate files. The best practice is to include the certificates directly within your Python app directory and manage them securely.
- Ensure that the paths to the certificates (root, client, and client key files) are correctly specified in your application code.
- Specify the path to the PEM files to establish the secure connection.

### 6. Qlik Sense Engine.ini configuration

- Engine\Settings.ini must be configured with: EnableTTL=1, SessionTTL=30

Ensure that these steps are carefully followed on both your local machine and the Qlik Sense server to establish a secure and functional API connection.

## Usage

**IMPORTANT NOTE**:
   - You need to open the app first from Qlik Sense. This action tells the engine to load the app into memory and create a session for you.
   - After the app is opened and the session is established, you can run the method `EvaluateEx` using the handle returned by your `OpenDoc` call.

1. Run the application to establish the API connection and perform the desired operations with Qlik Sense.
    ```bash
    python app.py
    ```
2. Refer to the [Examples](Examples.ipynb) for usage examples.
