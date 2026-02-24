# MCP VoipNow Calls - Complete Documentation

The VoipNow Calls MCP server delivers extensive call management and communication features for VoipNow platforms. It allows AI assistants to use the VoipNow UnifiedAPI to handle phone calls, call history, extensions, and fax operations.

This guide walks you through setting up and using the VoipNow Calls MCP server to manage calls, extensions, CDR records, and fax operations.

## Table of Contents

- [Key Capabilities](#key-capabilities)
  - [Call Management](#call-management)
  - [Extension Management](#extension-management)
  - [Communication Services](#communication-services)
  - [Available Tools Summary](#available-tools-summary)
- [Setup](#setup)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Command-Line Arguments](#command-line-arguments)
  - [Configuration File](#configuration-file)
- [Configuration](#configuration)
  - [VoipNow App Credentials](#voipnow-app-credentials)
  - [Container Support (Optional)](#container-support-optional)
  - [MCP Transport Setup](#mcp-transport-setup)
- [Tools Reference](#tools-reference)
  - [List CDR](#list-cdr)
  - [Phone Calls Create](#phone-calls-create)
  - [Phone Calls Delete](#phone-calls-delete)
  - [Phone Calls List](#phone-calls-list)
  - [Phone Calls Update Monitor](#phone-calls-update-monitor)
  - [Phone Calls Update OnHold/OffHold](#phone-calls-update-onholdoffhold)
  - [Phone Calls Update Park](#phone-calls-update-park)
  - [Phone Calls Update UnPark](#phone-calls-update-unpark)
  - [Phone Calls Update PickUp/BargeIn](#phone-calls-update-pickupbargein)
  - [Phone Calls Update Start/Stop Recording](#phone-calls-update-startstop-recording)
  - [Phone Calls Update Transfer](#phone-calls-update-transfer)
  - [Phone Calls Update Transfer to Voicemail](#phone-calls-update-transfer-to-voicemail)
  - [Phone Calls Update Whisper](#phone-calls-update-whisper)
  - [Extensions Presence List](#extensions-presence-list)
  - [Extensions Queue Agents List](#extensions-queue-agents-list)
  - [Extensions Queue Agents Update](#extensions-queue-agents-update)
  - [Extensions Phone Call Events Create](#extensions-phone-call-events-create)
  - [Extensions Phone Call Events List](#extensions-phone-call-events-list)
  - [Extensions Phone Call Events Update](#extensions-phone-call-events-update)
  - [Extensions Phone Call Events Delete](#extensions-phone-call-events-delete)
  - [Faxes Create](#faxes-create)
- [Error Handling](#error-handling)
  - [Error Categories](#error-categories)
  - [Common Solutions](#common-solutions)
  - [Debugging Tips](#debugging-tips)
  - [Support Resources](#support-resources)
- [Prompt Examples](#prompt-examples)
  - [How to Use This Guide](#how-to-use-this-guide)
  - [Writing Effective Prompts](#writing-effective-prompts)
  - [Error Prevention and Handling](#error-prevention-and-handling)
  - [Available Operations](#available-operations)
  - [Basic Operations](#basic-operations)
  - [Advanced Operations](#advanced-operations)
  - [Special Use Cases](#special-use-cases)
  - [Best Practices](#best-practices)
- [For Developers](#for-developers)
  - [Quick Start](#developer-quick-start)
  - [Basic Tool Template](#basic-tool-template)
  - [Naming Convention](#naming-convention)
  - [Common Patterns](#common-patterns)
  - [Documentation](#documentation)

---

## Key Capabilities

### Call Management

- Phone calls: create, delete, list, and manage active phone calls
- Call control: monitor, hold/unhold, park/unpark, transfer, and record calls
- Advanced operations: pickup, barge-in, whisper, and transfer to voicemail

### Extension Management

- Presence monitoring for extensions
- Queue agents list/update
- Phone call events create/list/update/delete

### Communication Services

- CDR records (history and statistics)
- Fax services
- Real-time call control

### Available Tools Summary

- `cdr-list`: Get the list of call history records from VoipNow.
- `phone-calls-create`: Create a phone call based on the input arguments.
- `phone-calls-delete`: Allows hanging up phone calls in particular contexts.
- `phone-calls-list`: Allows listing of phone call resources in particular contexts.
- `phone-calls-update-monitor`: Allows monitoring of a phone call.
- `phone-calls-update-onhold-offhold`: Put on hold/take off hold a phone call.
- `phone-calls-update-park`: Park a phone call.
- `phone-calls-update-unpark`: Retrieve a phone call from the parking lot.
- `phone-calls-update-pickup-bargein`: Pick up/barge in on a phone call.
- `phone-calls-update-start-stop-recording`: Start/stop recording of a phone call.
- `phone-calls-update-transfer`: Transfer a phone call.
- `phone-calls-update-transfer-tovoicemail`: Transfer a phone call to voicemail.
- `phone-calls-update-whisper`: Whisper on a phone call.
- `extensions-presence-list`: List the registration status of extensions.
- `extensions-queue-agents-list`: List all agents registered to a queue.
- `extensions-queue-agents-update`: Update the status of an agent.
- `extensions-phone-call-events-create`: Allows adding new phone call events.
- `extensions-phone-call-events-list`: Allows listing phone call events.
- `extensions-phone-call-events-update`: Allows updating existing phone call events.
- `extensions-phone-call-events-delete`: Allows deleting a phone call event.
- `faxes-create`: Allows sending faxes.

---

## Setup

### Requirements

| Component   | Minimum Version | Purpose                           |
| ----------- | --------------- | --------------------------------- |
| **Node.js** | `v18+`          | JavaScript runtime environment    |
| **VoipNow** | `5.6+`          | VoIP platform for API integration |
> `Note:` To run MCP Inspector, Node.js 22.7.5 or higher is required. Using Node 20 or lower will cause installation/runtime errors.

**Supported Operating Systems:**

<details>
<summary>Redhat OS</summary>

##### Node.js

Check which module for node is activated:

```bash
yum/dnf module list nodejs
```

Enable the version that is greater than or equal to the minimal requirement.

```bash
yum/dnf module enable nodejs:<version>
```

```bash
yum/dnf install nodejs npm
```

</details>

<details>
<summary>Debian OS</summary>

Minimal OS versions:

- Debian:
  - 12 ( Bookworm)
- Ubuntu:
  - 22.04 LTS

##### Node.js

```bash
apt update
apt install nodejs npm
```

</details>

<details>
<summary> macOS </summary>

##### Node.js

```bash
brew install node npm
```

</details>

<details>
<summary> Windows </summary>

##### Node.js

Get `Node.js` from [this link](https://nodejs.org/en/download/)

</details>

### Installation

**Quick Setup:**

```bash
# 1. Clone the repository
git clone <repository-url>

# 2. Navigate to VoipNow Calls directory
cd calls

# 3. Install dependencies
npm install

# 4. Build the project
npm run build
```

### Quick Start

Get VoipNow Calls MCP running and verified quickly.

1.  Create a minimal config.json

```json
{
  "appId": "your-app-id",
  "appSecret": "your-app-secret",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/abs/path/to/calls/.access_token",
  "logLevel": "info",
  "insecure": false
}
```

2. Verify with MCP Inspector (STDIO)

```bash
npx @modelcontextprotocol/inspector
```

- In Inspector, choose STDIO and set:
  - Command: `node`
  - Args: `["/abs/path/to/calls/dist/index.js", "--config", "/abs/path/to/config.json"]`
  - Connect, then click `List Tools` to confirm discovery

Notes:

- To run over HTTP later, start with: `node dist/index.js --transport streamable-http --port 3000 --config /abs/path/to/config.json` and connect to `http://SERVER_IP:3000/mcp`. For secured HTTP, add `--secure` and set `authTokenMCP` in `config.json`, then connect with `Authorization: Bearer YOUR_AUTH_TOKEN`.

### Command-Line Arguments

The server supports the following command-line arguments:

| Argument          | Short | Default     | Description                                       |
| ----------------- | ----- | ----------- | ------------------------------------------------- |
| `--transport`     | `-t`  | `stdio`     | Transport type: `stdio`, `sse`, `streamable-http` |
| `--port`          | `-p`  | `3000`      | Port number for HTTP transports                   |
| `--address`       | `-a`  | `localhost` | Address to listen on                              |
| `--secure`        | `-s`  | `false`     | Enable authorization for MCP server               |
| `--config`        | `-c`  | -           | Path to configuration file                        |
| `--log_transport` | `-l`  | `console`   | Log transport: `console` or `syslog`              |

### Configuration File

Create a `config.json` file with your VoipNow credentials:

```json
{
  "appId": "your-app-id",
  "appSecret": "your-app-secret",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/path/to/.access_token",
  "authTokenMCP": "your-mcp-auth-token",
  "logLevel": "info",
  "insecure": false
}

```
**Configuration parameters:**

| Parameter          | Required | Description                                           |
| ------------------ | -------- | ----------------------------------------------------- |
| `appId`            | yes      | Application ID from VoipNow App registration          |
| `appSecret`        | yes      | Application secret from VoipNow App registration      |
| `voipnowHost`      | yes      | VoipNow server URL (e.g., `https://your-voipnow-host.com`) |
| `voipnowTokenFile` | yes      | File path to store/read access token                  |
| `authTokenMCP`     | depends  | Auth token for MCP (required when `--secure` is used) |
| `logLevel`         | no       | Logging level: `debug`, `info`, `warning`, `error`    |
| `insecure`         | no       | Disable SSL verification (default: `false`). **NOT for production!** |

> [!NOTE]
> **Auto-reload**: The server automatically reloads its configuration when `config.json` or the token file is modified.

**Basic usage:**

```bash
# STDIO transport (local development)
node dist/index.js --config /path/to/config.json

# HTTP transport (remote access)
node dist/index.js --transport streamable-http --address 0.0.0.0 --port 3000 --config /path/to/config.json

# Enable authorization for HTTP transport
node dist/index.js --transport streamable-http --address 0.0.0.0 --port 3000 --secure --config /path/to/config.json
```

> [!CAUTION]
> **TLS Certificate Verification:** By default, the server requires valid SSL/TLS certificates when connecting to VoipNow. For development/testing with self-signed certificates, you can disable verification by setting `"insecure": true` in `config.json`. **This is NOT recommended for production** as it exposes you to man-in-the-middle attacks. For production, use valid certificates or terminate TLS through a trusted proxy.

---

## Configuration

This section explains how to set up VoipNow API credentials and configure the MCP server for best performance.

### VoipNow App Credentials

#### Step 1: VoipNow app registration

**Prerequisites:**

- VoipNow account with at least `Organization` role
- Permission to create Apps in VoipNow

**Registration process:**

1. **Access app registration**

   - Log in to VoipNow admin panel.
   - Navigate to: `Unified Communications` → `Integrations` → `Apps`
   - Click: `App Registration` → `Add App`

2. **Configure app settings**

   - Fill in all required fields with your app information.
   - **Important**: Enable `App is trusted` for seamless authentication.
     - This enables the app to authenticate using only the App Key and App Secret.
     - No additional user authentication required

3. **Save credentials**
   - Go to `App Registration` and locate your newly created app.
   - Record the following credentials:
     - `App ID/key`
     - `App secret`

> [!TIP]
> For detailed app registration instructions, see the [VoipNow Integration Guide](https://red.4psa.me/doc/hg/manual-integration/5.6.0/Register-App).

#### Step 2: Server configuration

**Create configuration file:**

Navigate to your VoipNow Calls MCP server directory and create/update `config.json`:

```json
{
  "appId": "your-app-id-here",
  "appSecret": "your-app-secret-here",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/path/to/calls/.access_token",
  "authTokenMCP": "your-mcp-auth-token",
  "logLevel": "info",
  "insecure": false
}
```

**Configuration example with real paths:**

```json
{
  "appId": "TiDvYAt",
  "appSecret": "2Wth79FkXOUVALaFJZPoBPSvShnUfo0e",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/home/user/mcp/calls/.access_token",
  "authTokenMCP": "KoMMbqUHaYXtBxh7XuJF09SZs",
  "logLevel": "info",
  "insecure": false
}
```

#### Step 3: Token management

**Automatic token generation:**

Start the server (with any transport) to automatically generate the initial access token:

```bash
# The server will create the token file if it doesn't exist.
# Example: HTTP (Streamable HTTP)
node dist/index.js --transport streamable-http --address 0.0.0.0 --port 3000 --config /path/to/config.json

# Example: STDIO
node dist/index.js --config /path/to/config.json
```

To generate a new token:

- Every 5 minutes, the VoipNow Calls MCP server automatically verifies whether the token is nearing expiration and generates a new one.

**Token file format:**

The token file referenced by `voipnowTokenFile` is a plain-text line with three colon-separated fields written in milliseconds:

```bash
<createdAtMs>:<expiresAtMs>:<accessToken>
```

Example:

```bash
1717081337123:1717082237123:eyJhbGciOi...
```

**Configuration change detection:**

The server monitors authentication-related configuration settings (`appId`, `appSecret`, or `voipnowHost`). When any of these change, it automatically deletes the token file so a new one is generated with the updated configuration. This allows smooth transitions when switching VoipNow servers or updating credentials, without needing to manually remove the token file.

Do not modify this file manually. It is created and refreshed by the server.

### Container Support (Optional)

> [!NOTE]
> Container support is optional and only needed if you want to run the MCP server in a Docker/Podman container.

The VoipNow Calls MCP server supports containerization for isolated deployments and easier scaling.

**Setup steps:**

1. **Prerequisites**

   ```bash
   # Ensure Docker or Podman is installed
   docker --version
   # OR
   podman --version
   ```

2. **Build container image**

   ```bash
   # Using Docker
   docker build -t voipnow-calls-mcp -f ./Containerfile .

   # Using Podman
   podman build -t voipnow-calls-mcp -f ./Containerfile .
   ```

3. **Prepare configuration**

   ```bash
   # Create config.json with container-appropriate paths
   cat > config.json << EOF
   {
     "appId": "your-app-id",
     "appSecret": "your-app-secret",
     "voipnowHost": "https://your-voipnow-host.com",
     "voipnowTokenFile": "/app/.access_token",
     "authTokenMCP": "your-mcp-auth-token",
     "logLevel": "info",
  "insecure": false
   }
   EOF
   ```

4. **Run container**

   ```bash
   # Using Docker
   docker run -d \
     --name voipnow-calls \
     -v $(pwd)/config.json:/app/config.json \
     -p 3000:3000 \
     voipnow-calls-mcp \
     -c /app/config.json -p 3000 -t streamable-http -a 0.0.0.0

   # Using Podman
   podman run -d \
     --name voipnow-calls \
     -v $(pwd)/config.json:/app/config.json:z \
     -p 3000:3000 \
     voipnow-calls-mcp \
     -c /app/config.json -p 3000 -t streamable-http -a 0.0.0.0
   ```

### MCP Transport Setup

Configure your MCP client to connect to the VoipNow Calls server using one of the supported transport methods.

#### STDIO transport

> [!NOTE]
> STDIO transport runs the server as a child process - no network configuration needed.

**Configuration:**

```json
{
  "mcpServers": {
    "mcp-voipnow-calls": {
      "command": "node",
      "args": [
        "/path/to/calls/dist/index.js",
        "--config",
        "/path/to/config.json"
      ]
    }
  }
}
```

**Placeholders to replace:**

- `/path/to/calls/dist/index.js` - The absolute path to the VoipNow Calls MCP server executable
- `/path/to/config.json` - The absolute path to your configuration file

#### HTTP transports

> [!IMPORTANT]
> Start the server before configuring the MCP client.

**Authentication requirements:**

- **Required**: When `--secure` flag is used
- **Not required**: For STDIO transport or unsecured HTTP
- **Note**: Some clients don't send `Authorization` headers during initialization

**Generate authentication token:**

```bash
# Generate a secure token (32+ characters recommended)
tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32 && echo
```

Add the generated token to your `config.json`:

```json
{
  ...
  "authTokenMCP": "your-generated-token-here"
  ...
}
```

> [!NOTE]
> Based on the client used, `url` could be replaced with `serverUrl`. (e.g: WindSurf)

##### Streamable HTTP (Recommended)

The VoipNow Calls MCP server must be started before you begin to configure the MCP client.

**Start Server:**

```bash
node dist/index.js --transport streamable-http --port 3000 --secure --config /path/to/config.json
```

**Client configuration:**

```json
{
  "mcpServers": {
    "voipnow-calls": {
      "url": "http://SERVER_IP:PORT/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_AUTH_TOKEN"
      }
    }
  }
}
```

**Placeholders to replace:**

- `SERVER_IP` - The IP address where the MCP server is running
- `PORT` - The port number on which the MCP server is listening (default: 3000)
- `YOUR_AUTH_TOKEN` - The authentication token generated for security

##### SSE (Legacy)

> [!WARNING]
> SSE transport is deprecated. Use Streamable HTTP for new deployments.

The VoipNow Calls MCP server must be started before you begin to configure the MCP client.

**Start server:**

```bash
node dist/index.js --transport sse --port 3000 --secure --config /path/to/config.json
```

**Client configuration:**

```json
{
  "mcpServers": {
    "voipnow-calls": {
      "url": "http://SERVER_IP:PORT/sse",
      "headers": {
        "Authorization": "Bearer YOUR_AUTH_TOKEN"
      }
    }
  }
}
```

**Placeholders to replace:**

- `SERVER_IP` - The IP address where the MCP server is running
- `PORT` - The port number on which the MCP server is listening (default: 3000)
- `YOUR_AUTH_TOKEN` - The authentication token generated for security

#### MCP Bundles (.mcpb)

To create a `.mcpb` file, you must first install the `mcpb` command:

```bash
npm install -g @anthropic-ai/mcpb
```

Since the `manifest.json` file is already created, go to the root folder of the VoipNow Calls MCP server and run:

```bash
mcpb pack
```

The command creates a `.mcpb` file, which can be used in `Claude Desktop` app. The `config.json` file must now be located on the same machine where `Claude Desktop` is running, and the path must be provided in `Extension` windows.

---

## Tools Reference

### List CDR

- **Tool Name**: `cdr-list`
- **Description**: Get the list of call history records from VoipNow.
- **Input Schema**:

| Parameter     | Type     | Description                                                     |
| ------------- | -------- | --------------------------------------------------------------- |
| ownerId       | string   | Filter by call owner (user/organization ID)                     |
| count         | string   | Number of records to retrieve (1-4999)                          |
| filterBy      | enum     | Filter field ("source", "destination", "published", "answered") |
| filterValue   | string   | Value to filter by                                              |
| source        | string   | Caller number (extension or public number)                      |
| destination   | string   | Called number (extension or public number)                      |
| startDate     | datetime | Start date for answered calls (ISO format)                      |
| endDate       | datetime | End date for answered calls (ISO format)                        |
| saveStartDate | datetime | Start date for saved calls (ISO format)                         |
| saveEndDate   | datetime | End date for saved calls (ISO format)                           |
| disposition   | enum     | Call disposition (0-5, see below)                               |
| flow          | enum     | Flow of the call (see below)                                    |
| fields        | string[] | Array of PhoneCallStat field names                              |
| startIndex    | string   | Start index of the paged                                        |
| sortOrder     | enum     | Records will be ordered by published                            |

**Disposition values:**

- 0: ANSWERED
- 1: BUSY
- 2: FAILED
- 3: NO ANSWER
- 4: UNKNOWN
- 5: NOT ALLOWED

**Flow values:**

- 2: a local call
- 4: an outgoing public call
- 8: an incoming public call

### Phone Calls Create

- **Tool Name**: `phone-calls-create`
- **Description**: Creates a phone call based on the input arguments.
- **Input Schema**:

| Parameter           | Type     | Description                                                                                           |
| ------------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| userId              | string   | ID of the user on whose behalf the phone call is made                                                 |
| type                | enum     | The type of the call                                                                                  |
| waitForPickup       | string   | The maximum number of seconds to wait until one of the phone numbers picks up                         |
| callDuration        | string   | Total duration of the call, in seconds                                                                |
| allowPublicTransfer | boolean  | This flag restricts or permits transfer of a phone call made to a phone number external to the system |
| video               | boolean  | Enable video support in SDP                                                                           |
| number              | string   | Represents the number of the scheduled conference                                                     |
| pin                 | string   | Represents the PIN of the scheduled conference                                                        |
| extension           | string   | Must refer to a phone terminal type extension                                                         |
| source              | string[] | Can be set to a list of extension numbers or public numbers                                           |
| destination         | string[] | Can be any extension number or a public number                                                        |
| callerId            | string   | The caller name and number. It is displayed to the source.                                            |
| callerDestination   | string   | The caller name and number. It is displayed to the destination.                                       |
| nonce               | string   | A unique string that allows to identify the call created based on the request                         |

### Phone Calls Delete

- **Tool Name**: `phone-calls-delete`
- **Description**: Allows you to hang up PhoneCalls in specific contexts.
- **Input Schema**:

| Parameter   | Type   | Description                                                       |
| ----------- | ------ | ----------------------------------------------------------------- |
| userId      | string | ID of the user that owns the extension involved in the phone call |
| extension   | string | Number of the extension involved in the call                      |
| phoneCallId | string | The ID of the phone call to be updated                            |
| phoneNumber | string | Phone number of one of the parties involved in the phone call     |

### Phone Calls List

- **Tool Name**: `phone-calls-list`
- **Description**: Allows listing of PhoneCalls resources in particular contexts.
- **Input Schema**:

| Parameter   | Type     | Description                                                                                  |
| ----------- | -------- | -------------------------------------------------------------------------------------------- |
| userId      | string   | ID of the user that owns the extension involved in the phone call                            |
| extension   | string   | Number of the extension involved in the call                                                 |
| phoneCallId | string   | The ID of the phone call to be updated                                                       |
| count       | string   | Number of records to retrieve (1-4999)                                                       |
| filterBy    | enum     | Filter field ("id", "published")                                                             |
| filterOp    | enum     | Filter field ("contains","equals","greaterThan","inArray","lessThan","present","startsWith") |
| filterValue | string   | The value to filter by. You can filter by the phone call ID or the published date            |
| startIndex  | string   | Start index of the paged                                                                     |
| fields      | string[] | Array of PhoneCall field names                                                               |
| sortOrder   | enum     | The records are always ordered by their publish time.                                        |

### Phone Calls Update Monitor

- **Tool Name**: `phone-calls-update-monitor`
- **Description**: Allows monitoring on a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                                                                                 |
| --------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call                                                           |
| extension       | string | Number of the extension involved in the call                                                                                |
| phoneCallId     | string | The ID of the phone call to be updated                                                                                      |
| action          | enum   | The action to be performed on the phone call (Monitor)                                                                      |
| sendCallTo      | string | The number of the extension that will monitor. Must be in the same organization as the extension given in the URI-Fragment. |
| callerId        | string | The caller name and number. It is displayed to the source.                                                                  |
| waitForPickup   | string | The maximum number of seconds to wait until one of the phone numbers picks up                                               |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                                                                             |

### Phone Calls Update OnHold/OffHold

- **Tool Name**: `phone-calls-update-onhold-offhold`
- **Description**: Allows to 'put on hold'/'take off from hold' a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                       |
| --------------- | ------ | ----------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call |
| extension       | string | Number of the extension involved in the call                      |
| phoneCallId     | string | The ID of the phone call to be updated                            |
| action          | enum   | The action to be performed on the phone call (OnHold/OffHold)     |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                   |

### Phone Calls Update Park

- **Tool Name**: `phone-calls-update-park`
- **Description**: Allows you to park a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                       |
| --------------- | ------ | ----------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call |
| extension       | string | Number of the extension involved in the call                      |
| phoneCallId     | string | The ID of the phone call to be updated                            |
| action          | enum   | The action to be performed on the phone call (Park)               |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                   |
| maxInParking    | number | The time interval during which the call stays in the parking lot  |

### Phone Calls Update UnPark

- **Tool Name**: `phone-calls-update-unpark`
- **Description**: Allows to retrieve a phone call from the parking lot.
- **Input Schema**:

| Parameter       | Type   | Description                                                                        |
| --------------- | ------ | ---------------------------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call                  |
| extension       | string | Number of the extension involved in the call                                       |
| phoneCallId     | string | The ID of the phone call to be updated                                             |
| action          | enum   | The action to be performed on the phone call (UnPark)                              |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                                    |
| sendCallTo      | string | The number of the extension that connects to the parked phone call                 |
| callerId        | string | The caller name and number. It is displayed to the source.                         |
| waitForPickup   | string | The maximum number of seconds to wait until one of the phone numbers picks up      |

### Phone Calls Update PickUp/BargeIn

- **Tool Name**: `phone-calls-update-pickup-bargein`
- **Description**: Allows to 'pick up'/'barge in on' a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                                        |
| --------------- | ------ | ---------------------------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call                  |
| extension       | string | Number of the extension involved in the call                                       |
| phoneCallId     | string | The ID of the phone call to be updated                                             |
| action          | enum   | The action to be performed on the phone call (PickUp/BargeIn)                      |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                                    |
| sendCallTo      | string | PickUp: Number of the Extension that connects to the parked phone call; BargeIn: Number of the extension that will barge in. Must be in the same organization as the extension given in the URI-Fragment. |
| callerId        | string | The caller name and number. It is displayed to the source                          |
| waitForPickup   | string | The maximum number of seconds to wait until one of the phone numbers used picks up |

### Phone Calls Update Start/Stop Recording

- **Tool Name**: `phone-calls-update-start-stop-recording`
- **Description**: Allows to 'start a recording'/'stop the recording' of a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                                 |
| --------------- | ------ | --------------------------------------------------------------------------- |
| userId          | string | ID of the user that owns the extension involved in the phone call           |
| extension       | string | Number of the extension involved in the call                                |
| phoneCallId     | string | The ID of the phone call to be updated                                      |
| action          | enum   | The action to be performed on the phone call (StartRecording/StopRecording) |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                             |
| format          | enum   | The recording format (wav/wav49)                                            |

### Phone Calls Update Transfer

- **Tool Name**: `phone-calls-update-transfer`
- **Description**: Allows to transfer a phone call.
- **Input Schema**:

| Parameter          | Type   | Description                                                                                   |
| ------------------ | ------ | --------------------------------------------------------------------------------------------- |
| userId             | string | ID of the user that owns the extension involved in the phone call                             |
| extension          | string | Number of the extension involved in the call                                                  |
| phoneCallId        | string | The ID of the phone call to be updated                                                        |
| action             | enum   | The action to be performed on the phone call (Transfer)                                       |
| sendCallTo         | string | Phone number where the call is transferred to. Can be an extension number or a public number. |
| transferFromNumber | string | The phone number of the party that transfers the call                                         |
| transferNumber     | string | The phone number of the party being transferred                                               |

### Phone Calls Update Transfer to Voicemail

- **Tool Name**: `phone-calls-update-transfer-tovoicemail`
- **Description**: Allows to transfer a phone call to voicemail.
- **Input Schema**:

| Parameter          | Type   | Description                                                                 |
| ------------------ | ------ | --------------------------------------------------------------------------- |
| userId             | string | ID of the user that owns the extension involved in the phone call           |
| extension          | string | Number of the extension involved in the call                                |
| phoneCallId        | string | The ID of the phone call to be updated                                      |
| action             | enum   | The action to be performed on the phone call (TransferToVoicemail) |
| sendCallTo         | string | Number of the extension where the phone call should be transferred to. Must be in the same organization as the extension given in the URI-Fragment, and it must be multi-user aware. |
| transferFromNumber | string | The phone number of the party that transfers the call                       |
| transferNumber     | string | The phone number of the party being transferred                             |

### Phone Calls Update Whisper

- **Tool Name**: `phone-calls-update-whisper`
- **Description**: Allows a third-party to whisper into a phone call.
- **Input Schema**:

| Parameter       | Type   | Description                                                                                                        |
| --------------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| userId          | string | ID of the user that owns the extension involved in the phone call                                                  |
| extension       | string | Number of the extension involved in the call                                                                       |
| phoneCallId     | string | The ID of the phone call to be updated                                                                             |
| action          | enum   | The action to be performed on the phone call (Whisper)                                                             |
| sendCallTo      | string | Number of the extension that will whisper.                                                                         |
| callerId        | string | The caller name and number. It is displayed to the source.                                                         |
| waitForPickup   | string | The maximum number of seconds to wait until one of the phone numbers picks up                                      |
| phoneCallViewId | string | The PhoneCallView that is subject to the update                                                                    |
| privateW        | enum   | When set to 1, the extension that whispers does not hear the conversation between the parties involved in the call |

### Extensions Presence List

- **Tool Name**: `extensions-presence-list`
- **Description**: Allows you to list the extensions registration status.
- **Input Schema**:

| Parameter   | Type     | Description                                                                  |
| ----------- | -------- | ---------------------------------------------------------------------------- |
| userId      | string   | ID of the user that owns the extensions for which the presence is returned.  |
| extension   | string   | Extended number of a phone terminal extension                                |
| count       | string   | Number of records to retrieve (1-4999)                                       |
| filterBy    | enum     | Filter field ("extension").                                                  |
| filterOp    | enum     | Filter field ("contains", "equals", "inArray", "startsWith")                 |
| filterValue | string   | Value to filter by                                                           |
| startIndex  | string   | Start index of the paged                                                     |
| fields      | string[] | Array of ExtensionPresence field names                                       |
| sortOrder   | enum     | Records will be ordered by the number of the extension.                      |

### Extensions Queue Agents List

- **Tool Name**: `extensions-queue-agents-list`
- **Description**: Listing all the agents that are registered to a queue.
- **Input Schema**:

| Parameter   | Type     | Description                                                    |
| ----------- | -------- | -------------------------------------------------------------- |
| userId      | string   | ID of the user that owns the queue                             |
| extension   | string   | Number of the queue extension                                  |
| agent       | string   | Identifier of the queue agent                                  |
| count       | string   | Number of records to retrieve (1-4999)                         |
| filterBy    | enum     | Filter fields: ("agentNumber", "queue", "status")              |
| filterOp    | enum     | Filter fields: ("contains", "equals", "present", "startsWith") |
| filterValue | string   | Value to filter by                                             |
| startIndex  | string   | Start index of the paged                                       |
| fields      | string[] | Array of Phone Call Event field names                          |
| sortOrder   | enum     | Records will be ordered by status.                             |

### Extensions Queue Agents Update

- **Tool Name**: `extensions-queue-agents-update`
- **Description**: Updating the statuses of agents that are registered to a queue.
- **Input Schema**:

| Parameter | Type   | Description                          |
| --------- | ------ | ------------------------------------ |
| userId    | string | ID of the user that owns the queue.  |
| extension | string | Number of the queue extension        |
| agent     | string | Identifier of the queue agent        |
| status    | enum   | The status of the agent (0,1,2)      |

**Status values:**

- 0: Logged out
- 1: Online
- 2: Paused

### Extensions Phone Call Events Create

- **Tool Name**: `extensions-phone-call-events-create`
- **Description**: Allows you to add new phone call events.
- **Input Schema**:

| Parameter | Type   | Description                                                                                                                  |
| --------- | ------ | ---------------------------------------------------------------------------------------------------------------------------- |
| userId    | string | ID of the user that owns the extension for which the event is added.                                                         |
| extension | string | Number of the extension for which the event is added.                                                                        |
| type      | enum   | Type of the Phone Call Event (0,1,2,3,4)                                                                                     |
| method    | enum   | The HTTP method used by the server to access the URL when an event occurs (0,1)                                              |
| note      | string | Notes about the event                                                                                                        |
| url       | string | The URL that is accessed when the extension receives, makes, or terminates a phone call. Must be encoded using the RFC 3986. |
| status    | enum   | The status of the event (0,1)                                                                                                |

**Type values:**

- 0: Dial-in
- 1: Dial-out
- 2: Hangup
- 3: Answer incoming call
- 4: Answer outgoing call

**Method values:**

- 0: GET
- 1: POST

**Status values:**

- 0: disabled
- 1: enabled

### Extensions Phone Call Events List

- **Tool Name**: `extensions-phone-call-events-list`
- **Description**: Allows you to list the phone call events.
- **Input Schema**:

| Parameter   | Type     | Description                                                                                            |
| ----------- | -------- | ------------------------------------------------------------------------------------------------------ |
| userId      | string   | ID of the user that owns the extension for which the event is listed.                                  |
| extension   | string   | Number of the Extension for which the event is listed.                                                 |
| eventType   | enum     | Type of the Phone Call Event. If missing, events for all the types are returned (0,1,2,3,4)            |
| eventID     | string   | The ID of the phone call event to be updated                                                           |
| count       | string   | The size of the chunk to retrieve                                                                      |
| filterBy    | enum     | Records can be filtered by ("id", "method", "modified", "note", "status", "type", "url")               |
| filterValue | string   | The value to filter by                                                                                 |
| startIndex  | string   | The start index of the paged collection                                                                |
| fields      | string[] | An array of Phone Call Event field names. For standard values, please see the PhoneCallEvent resource. |
| sortOrder   | enum     | Records will be ordered by url.                                                                        |

**Event type values:**

- 0: Dial-in
- 1: Dial-out
- 2: Hangup
- 3: Answer incoming call
- 4: Answer outgoing call

### Extensions Phone Call Events Update

- **Tool Name**: `extensions-phone-call-events-update`
- **Description**: Allows you to update existing phone call events.
- **Input Schema**:

| Parameter | Type   | Description                                                                                                                  |
| --------- | ------ | ---------------------------------------------------------------------------------------------------------------------------- |
| userId    | string | ID of the user that owns the extension for which the event is updated                                                        |
| extension | string | Number of the extension for which the event is updated                                                                       |
| eventType | enum   | Type of the Phone Call Event                                                                                                 |
| eventID   | string | The ID of the phone call event to be updated                                                                                 |
| method    | enum   | The HTTP method used by the server to access the URL when an event occurs (0,1)                                              |
| note      | string | Notes about the event (0,1,2,3,4)                                                                                            |
| url       | string | The URL that is accessed when the extension receives, makes, or terminates a phone call. Must be encoded using the RFC 3986. |
| status    | enum   | The status of the event (0,1)                                                                                                |

**Event type values:**

- 0: Dial-in
- 1: Dial-out
- 2: Hangup
- 3: Answer incoming call
- 4: Answer outgoing call

**Method values:**

- 0: GET
- 1: POST

**Status values:**

- 0: disabled
- 1: enabled

### Extensions Phone Call Events Delete

- **Tool Name**: `extensions-phone-call-events-delete`
- **Description**: Allows you to delete a phone call event.
- **Input Schema**:

| Parameter | Type   | Description                                                                                            |
| --------- | ------ | ------------------------------------------------------------------------------------------------------ |
| userId    | string | ID of the user that owns the extension for which the event is deleted                                  |
| extension | string | Number of the extension for which the event is deleted                                                 |
| eventType | enum   | Type of the Phone Call Event (0,1,2,3,4)                                                               |
| eventID   | string | The ID of the phone call event to be updated. When missing, all events for that extension are deleted. |

**Event Type values:**

- 0: Dial-in
- 1: Dial-out
- 2: Hangup
- 3: Answer incoming call
- 4: Answer outgoing call

### Faxes Create

- **Tool Name**: `faxes-create`
- **Description**: Allows users to send faxes.
- **Input Schema**:

| Parameter  | Type     | Description                                       |
| ---------- | -------- | ------------------------------------------------- |
| userId     | string   | ID of the user on whose behalf the fax is sent    |
| extension  | string   | Number of the extension sending the fax           |
| recipients | string[] | The recipients of the fax                         |
| filePath   | string   | The path to the file that will be sent            |

---

## Error Handling

The VoipNow Calls MCP server offers robust error handling and detailed diagnostics to simplify troubleshooting.

### Error Categories

#### Configuration errors

- **Missing credentials**: App ID or App Secret not provided
- **Invalid configuration**: Malformed JSON or missing required fields
- **File access issues**: Token file path not accessible or writable

#### Authentication errors

- **Token generation failed**: Invalid app credentials or VoipNow server unavailable
- **Token expired**: Access token needs renewal (handled automatically)
- **MCP authorization failed**: Invalid or missing MCP auth token

#### API communication errors

- **Connection timeout**: VoipNow server not responding
- **Network issues**: DNS resolution or routing problems
- **API rate limiting**: Too many requests in a short timeframe

#### Validation errors

- **Invalid parameters**: Missing required fields or invalid data types
- **Call not found**: Specified phone call doesn't exist or has ended
- **Permission denied**: Insufficient privileges for requested operation

### Common Solutions

| Error Type                  | Solution                                              |
| --------------------------- | ----------------------------------------------------- |
| **Configuration errors**    | Verify `config.json` syntax and file permissions      |
| **Authentication failures** | Check app credentials and VoipNow connectivity        |
| **API timeouts**            | Verify network connectivity and VoipNow server status |
| **Parameter validation**    | Review tool documentation for required parameters     |
| **Permission errors**       | Make sure VoipNow account has sufficient privileges   |

### Debugging Tips

**Enable debug logging:**

```json
{
  "logLevel": "debug"
}
```

**Check server logs:**

```bash
# For console output
node dist/index.js --log_transport console --config /path/to/config.json

# For syslog output
node dist/index.js --log_transport syslog --config /path/to/config.json
```

**Validate configuration:**

```bash
# Test configuration without starting the server
node -e "
const config = require('/path/to/config.json');
console.log('Configuration valid:', !!(config.appId && config.appSecret));
"
```

### Support Resources

- **VoipNow API documentation**: Check official VoipNow API guides
- **Server logs**: Monitor application logs for detailed error information
- **Network diagnostics**: Use tools like `curl` to test connectivity to VoipNow API
- **Configuration validation**: Verify JSON syntax and required parameters

---

## Prompt Examples

### How to Use This Guide

This guide explains how to manage VoipNow calls with AI tools. Each example illustrates how to create prompts that the AI understands and processes accurately.

### Writing Effective Prompts

Every prompt must include these components:

1. Extension information:
   - Always use full extension format: 0003*xxx
   - Include client ID with leading zeros (e.g., 0003).
   - Example: "0003*001" not just "001"

2. Action details:
   - What operation you want to perform
   - Which calls to affect (current, all, specific)
   - Any conditions or filters

3. Safety measures:
   - Ask to verify call existence before actions.
   - Request confirmation after important changes.
   - Include status checks between steps.

4. For external numbers:
   - Always use full international format.
   - Include country code: +{country}{area}{number}
   - Example: "+14155552671" not "4155552671"

Here's a complete prompt example showing all components:
```
"On extension 0003*001:
1. Verify if there are any active calls
2. For the call with +14155552671:
   - Put it on hold
   - Confirm hold status before proceeding
   - Start recording if hold is successful
3. Tell me if any step fails"
```

### Error Prevention and Handling

1. Input validation
   - Always validate extension format before operations: `0003*xxx`
   - Verify external numbers have country code: `+{country}{area}{number}`
   - Double-check that all numbers match your intended targets.

2. Operation safety
   - Verify call existence before any action.
   - Check call state between operations.
   - Request confirmation after critical changes.
   - Include fallback instructions for failures.

3. Common error scenarios
   a. When Call Not Found:
      - "Check if the call still exists on 0003*001"
      - "List all active calls on the extension"
      - "Verify if the call was completed or transferred"

   b. When operation fails:
      - "Check the current call state"
      - "Verify extension permissions"
      - "Try alternative methods if available"

   c. When dealing with multiple calls:
      - "Identify specific calls by their properties"
      - "Handle one call at a time"
      - "Verify each operation before moving to next"

4. Recovery steps
   - Always include verification steps.
   - Request status reports after operations.
   - Plan for alternative actions if primary fails.
   - Example: "If hold fails, try to monitor the call instead"

#### Basic structure example

Here's a complete example showing all components:

```
"I need to monitor calls on extension 0003*042:
1. Check if there are any active calls
2. If found, start silent monitoring and send the call to 0003*001
3. If the operation fails, check if the calls are still active
4. Verify the monitoring status"
```

### Available Operations

All extensions must follow the format: `{clientId}*{extensionNumber}`
Example: `0003*001` where:
- 0003 is the client ID (including leading zeros)
- * is the separator
- 001 is the extension number

### Basic Operations

#### 1. Checking calls

a. Quick status check
```
"Show me any active calls on extension 0003*001"
```

b. Detailed call information
```
"For extension 0003*001:
1. List all active calls
2. Show me the duration of each call
3. Indicate which are internal vs external
4. Include the call states (on hold, recording, etc.)"
```

c. Targeted call search
```
"On extension 0003*001:
1. Find any calls with number +14155552671
2. Check if they're still active
3. Show me their current status"
```

#### 2. Making calls

a. Internal call (extension to extension)
```
"Please:
1. Verify if extension 0003*001 is available
2. Place a call to extension 0003*002
3. Let me know when it connects"
```

b. External call with verification
```
"For extension 0003*001:
1. Check if the line is free
2. Call +14155552671
3. Monitor the connection status
4. Tell me when the call is established"
```

c. Supervised call setup
```
"Help me set up a call:
1. From extension 0003*001
2. To number +14155552671
3. Start recording when connected
4. Let me monitor the conversation, send the call to 0003*004
5. Alert me if the call drops"
```

### Advanced Operations

#### 3. Call supervision

Simple monitoring:
```
"Start silent monitoring of the current call on extension 0003*002 and send the call to 0003*004"
```

Complete supervision scenario:
```
"Monitor extension 0003*002. When a call starts, begin silent monitoring and send the call to 0003*004.
If the agent needs help, let me whisper to them. If there's an emergency,
I need to be able to join the call immediately."
```

#### 4. Call control

Simple hold:
```
"Put the current call on extension 0003*001 on hold"
```

Multiple actions:
```
"On extension 0003*001:
1. Put the current call on hold
2. Start recording the call
3. After recording starts, transfer it to extension 0003*003
4. Verify each step was successful"
```

These examples work with tools for: call control (hold/unhold), call recording, and call transfers.

#### 5. Ending calls

Simple end:
```
"End the current call on extension 0003*001"
```

Safe end with verification:
```
"On extension 0003*001:
1. Check if the call is still active
2. End the call
3. Verify the call was disconnected"
```

#### 6. Call history

Simple history:
```
"Show me all calls from the last hour on extension 0003*001"
```

Detailed history:
```
"Show me call history for extension 0003*001 from the last hour with these details:
1. List all calls longer than 5 minutes
2. Show any missed calls
3. Include both internal and external calls
4. Sort by duration"
```

### Special Use Cases

#### 7. Problem management

Simple problem check:
```
"Find and disconnect any active calls to number 47723366"
```

Complete problem investigation:
```
"I need to investigate calls to/from 47723366:
1. Check which extensions have contacted this number recently
2. Find any active calls with this number
3. Disconnect those calls if found
4. Show me the call history pattern for this number
5. Verify all problematic calls are ended"
```

#### 8. Bulk operations

Simple bulk action:
```
"Put all calls longer than 60 minutes on hold"
```

Targeted bulk management:
```
"Find all active calls that:
1. Are longer than 60 minutes
2. Are not to our support extensions (0003*200 to 0003*299)
Then for each call:
1. Put it on hold
2. Verify the hold status
3. Show me the list of affected calls"
```

#### 9. Emergency supervision

Simple supervision:
```
"Monitor and record all calls on extension 0003*042"
```

Complete emergency handling:
```
"I need full supervision control of extension 0003*042:
1. List all active calls on the extension
2. Start recording the current call
3. Start silent monitoring and send the call to 0003*001
4. Whisper to the agent on the current call
5. Barge in to the call if needed"
```

### Best Practices

For all operations:
1. Always verify extension format (0003*xxx) before any action.
2. Include country code for external numbers (+1XXXXXXXXXX).
3. Verify successful completion of each action.
4. When in doubt, check if calls are still active before acting.

For secure operations:
- Before any operation, validate extension format (0003*xxx) with phone-calls-list.
- Use phone-calls-update-monitor and cdr-list to track all supervision activities.
- When calling external numbers, use phone-calls-create with full international format.
- Before recording calls, verify compliance using phone-calls-update-start-stop-recording.

---

## For Developers

### Developer Quick Start

Create new tools in `/src/tools/` using the naming pattern `{tool-name}.ts`.

### Basic Tool Template

```typescript
import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

export const yourToolName = "your-tool-name";
export const yourToolDescription = "Description of what your tool does.";

// Schema
export const YourToolSchema = z.object({
    userId: z.string().describe("Id of the User. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    requiredParam: z.string().describe("Description of this parameter."),
    optionalParam: z.string().optional().describe("Optional parameter description."),
}).strict();

// Tool
export const YOUR_TOOL: Tool = {
    name: yourToolName,
    description: yourToolDescription,
    inputSchema: zodToJsonSchema(YourToolSchema) as ToolInput,
}

// Implementation
export async function runYourTool(
    args: z.infer<typeof YourToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, requiredParam, optionalParam } = YourToolSchema.parse(args);

    try {
        logger.info(`Running ${yourToolName} tool...`);

        // Handle userId format
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Build URL path
        let urlPath = `/uapi/endpoint/`;
        if (modifiedUserId) {
            urlPath += `${modifiedUserId}/`;
        }

        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, urlPath), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': userAgent.toString(),
                'Authorization': `Bearer ${config.voipnowToken}`
            },
            redirect: 'manual'
        });

        // Error handling
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 400 || response.status === 401 || response.status === 403 || response.status === 500) {
                const errorMessage = `{'code': ${errorData.error.code}, 'message': ${errorData.error.message}}`
                throw new Error(errorMessage);
            }
            const errorMessage = `{'status': ${response.status}, 'statusText': ${response.statusText}}, 'body': ${JSON.stringify(errorData.error)}}`
            throw new Error(errorMessage);
        }

        const responseData = await response.json();
        return {
            content: [{ type: "text", text: JSON.stringify(responseData) }],
        };
    } catch (error) {
        const errorMessage = `Error in ${yourToolName}: ${error instanceof Error ? error.message : String(error)}`
        logger.error(errorMessage);
        return {
            content: [{ type: "text", text: errorMessage }],
        };
    }
}
```

### Naming Convention

- File: `tool-name.ts`
- Tool name: `toolName`
- Description: `toolDescription`
- Schema: `ToolSchema`
- Constant: `TOOL_NAME`
- Function: `runToolName`

### Common Patterns

**Schema types:**
```typescript
z.string().describe("String parameter")
z.string().optional().describe("Optional parameter")
z.string().default("@me").describe("Default value parameter")
z.enum(["VALUE1", "VALUE2"]).describe("Enum values")
z.array(z.string()).describe("Array of strings")
z.string().datetime({ local: true }).describe("DateTime parameter")
```

**Query parameters with validation:**
```typescript
let queryParams: utils.QueryParam[] = [
    { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
    { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
];

const errors: string[] = [];
for (const param of queryParams) {
    if (param.value) {
        if (param.validate && !param.validate(param.value)) {
            errors.push(`${param.name}: ${param.errorMessage}`);
        }
        paramsURL.append(param.name, param.value);
    }
}

if (errors.length > 0) {
    throw new Error(`Error validating query parameters: ${errors.join('; ')}`);
}
```

**Always use:**

- `utils.createUrl()` for URL building
- `.strict()` on schemas
- Standard error handling with `errorData.error.code`
- UserId format handling for @me, @viewer, @owner
- Consistent logging and validation patterns

### Documentation

Add new tools to `/doc/3-tools.md` following the existing format.

> [!CAUTION]
> The dynamic tool discovery system **requires** exact naming patterns. Tools that don't follow these patterns **will not be loaded**.

#### Required Exports (all must be present)

- `export const {toolName}ToolName = "exact-tool-name"`
- `export const {toolName}ToolDescription = "description"`
- `export const {ToolName}ToolSchema = z.object({...})`
- `export const {TOOLNAME}_TOOL: Tool = {...}`
- `export async function run{ToolName}Tool(...) {...}`

#### Example for a tool named "user-list"

- `userListToolName = "user-list"`
- `userListToolDescription = "Lists users"`
- `UserListToolSchema`
- `USER_LIST_TOOL`
- `runUserListTool`

---

**End of Documentation**
