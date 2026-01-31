# Test Directory Documentation

This directory includes test scripts for validating the functionality of different MCP VoipNow tools. Each script targets specific features to verify correct behavior under various scenarios.The following section describes each script and its purpose.

## Scripts

### `test_cdr_list_ai.py`

Tests the `cdr-list` tool, which retrieves call detail records (CDRs) based on various filters such as source, destination, and time range. This script verifies that the tool properly retrieves and processes CDR data.

### `test_class.py`

Contains a collection of test cases for multiple tools, including parking/unparking, holding/unholding, recording, and monitoring calls. This script serves as a central testing hub for core functionalities.

### `test_phone_calls_create_ai.py`

Tests the `phone-calls-create` tool, which initiates phone calls. The script validates the creation of simple phone calls and conference calls, ensuring proper parameter handling and call initiation.

### `test_phone_calls_delete_ai.py`

Tests the `phone-calls-delete` tool, which terminates active phone calls. This script ensures that calls are properly ended and verifies error handling for invalid or non-existent calls.

### `test_phone_calls_hold_ai.py`

Tests the `phone-calls-update-onhold-offhold` tool, which manages the hold/unhold state of phone calls. The script validates transitions between hold and active states and handles transient API errors.

### `test_phone_calls_list_ai.py`

Tests the `phone-calls-list` tool, which retrieves a list of active or historical phone calls. This script ensures accurate filtering and data retrieval based on provided parameters.

### `test_phone_calls_monitor_ai.py`

Tests the `phone-calls-update-monitor` tool, which allows monitoring of active phone calls. The script tests monitoring functionality and gracefully manages errors such as `access_denied`.

### `test_phone_calls_park_ai.py`

Tests the `phone-calls-update-park` and `phone-calls-update-unpark` tools, which park and unpark phone calls respectively. The script ensures proper tracking of parked calls and validates timeout handling.

### `test_phone_calls_recording_ai.py`

Tests the `phone-calls-update-start-stop-recording` tool, which starts and stops call recordings. The script ensures correct parameter handling and validates recording functionality.

### `test_phone_calls_transfer_ai.py`

Tests the `phone-calls-update-transfer` and `phone-calls-update-transfer-tovoicemail` tools, which transfer calls to other destinations or to voicemail respectively. The script validates transfer functionality and error handling for invalid transfers.

## Requirements

To run these tests, make sure the necessary dependencies are installed. If not, use the `requirements.txt` file to install them:

```bash
pip install -r requirements.txt
```

## Prerequisites

1. **Valid VoipNow server**:

   - Ensure you have access to a valid VoipNow server.
   - Obtain the following details from your server administrator:
     - Server URL
     - App ID
     - App Secret

2. **Config file**:

   - Add in `config.json` file in the project root directory with the following variables:

   ```json
   {
     "appId":"<app_id>",
     "appSecret":"<app_secret>",
     "voipnowHost":"<voipnow_host>",
     "voipnowTokenFile":"<path_to_token_file>/.access_token",
     "authTokenMCP":"<auth_token>",
     "logLevel":"<log_level>"
   }
   ```

3. **Environment variables**:

   - Create a `.env` file in the project root directory with the following variables:

       ```env
       TEST_EXTENSION=<Your test extension>
       TEST_DESTINATION=<Your test destination>
       OPENAI_API_KEY=<Your OpenAI API key>
       OPENAI_BASE_URL=<Your OpenAI base URL>
       OPENAI_MODEL=<Your OpenAI model name, e.g., gpt-4o-mini>
       OPENAI_MAX_TOKENS=<Maximum tokens for responses, e.g., 1000>
       OPENAI_TEMPERATURE=<Temperature for AI responses, e.g., 0.7>
       ```

   - Replace the placeholders with actual values.

4. **Python environment**:
   - Follow the setup instructions for Python 3.12 and virtual environment (venv) as described below.

## Setup instructions for Python 3.12

To set up the test environment with Python 3.12 and a virtual environment (venv), follow these steps:

1. **Install Python 3.12**:
   On AlmaLinux/RHEL/CentOS:

   ```bash
   sudo dnf install -y python3.12 python3.12-pip
   ```

   On Ubuntu/Debian:

   ```bash
   sudo apt update && sudo apt install -y python3.12 python3.12-venv python3.12-pip
   ```

2. **Create a virtual environment**:

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Build the MCP Server**:
   Before running tests, ensure the TypeScript MCP server is built:

   ```bash
   cd .. # Go back to project root
   npm install
   npm run build
   cd test # Return to test directory
   ```

5. **Run tests**:
   Activate the virtual environment and run the desired test script:

   ```bash
   source venv/bin/activate
   python <script_name>.py
   ```

Replace `<script_name>` with the name of the test script you want to execute.

---

For additional help, consult the official Python documentation or visit the AlmaLinux/Ubuntu support forums.

## Usage

Run individual test scripts from the source root using the following command:

```bash
./test/<script_name>.py
```

Replace `<script_name>` with the name of the script you want to execute.

The script must have executable permissions. If not, add them with:

```bash
chmod +x ./test/<script_name>.py
```

## Notes

- Ensure that the MCP VoipNow tools are properly configured and accessible before running the tests.
- Some tests may require specific permissions or active calls to function correctly.

---

For more information, see the documentation for each tool in the `src/tools` directory.
