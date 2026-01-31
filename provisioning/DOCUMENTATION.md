# VoipNow Provisioning MCP Server - Complete Documentation

The VoipNow Provisioning MCP server provides robust service provisioning and entity management for VoipNow platforms. It allows AI assistants to interact with the VoipNow API to manage users, organizations, service providers, and their related configurations.

---

## Table of Contents

1. [Key Capabilities](#key-capabilities)
   - [Entity Management](#entity-management)
   - [Permission & Limit Management](#permission--limit-management)
   - [Extension Management](#extension-management)
   - [Advanced Operations](#advanced-operations)
   - [Available Tools Summary](#available-tools-summary)
2. [Setup](#setup)
   - [Requirements](#requirements)
   - [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Command-Line Arguments](#command-line-arguments)
   - [Configuration File](#configuration-file)
3. [Configuration](#configuration)
   - [VoipNow App Credentials](#voipnow-app-credentials)
   - [Container Support (Optional)](#container-support-optional)
   - [MCP Transport Setup](#mcp-transport-setup)
4. [Tools Reference](#tools-reference)
   - [Entity](#entity)
   - [Billing](#billing)
   - [Extension](#extension)
   - [PBX](#pbx)
   - [Report](#report)
   - [Channel](#channel)
5. [Error Handling](#error-handling)
   - [Error Categories](#error-categories)
   - [Common Solutions](#common-solutions)
   - [Debugging Tips](#debugging-tips)
6. [Prompt Examples](#prompt-examples)
   - [How to Use This Guide](#how-to-use-this-guide)
   - [Basic Entity Management](#basic-entity-management-examples)
   - [Complex Provisioning Scenarios](#complex-provisioning-scenarios)
   - [User Management](#user-management)
   - [Extension Management Examples](#extension-management-examples)
   - [Charging Plan Management](#charging-plan-management)
   - [Complete Provisioning Example](#complete-provisioning-example)
7. [For Developers](#for-developers)
   - [Tool Templating Guide](#tool-templating-guide)
   - [Basic Tool Template](#basic-tool-template)
   - [Advanced Tool Template](#advanced-tool-template)

---

## Key Capabilities

### Entity Management

- **Users**: Create, edit, delete, and manage user accounts
- **Organizations**: Manage organizational structures and hierarchies
- **Service Providers**: Handle service provider configurations and settings

### Permission & Limit Management

- **Access control**: Set control panel access and user roles
- **Resource limits**: Configure extension limits, storage quotas, and concurrent call limits
- **Permission sets**: Manage feature permissions and administrative rights

### Extension Management

- **Extension types**: Support for phone terminal, queue, IVR, voicemail, conference, and other extension types
- **Configuration**: Set up extension parameters, passwords, and labels
- **Bulk operations**: Retrieve and manage multiple extensions

### Advanced Operations

- **Organizational movement**: Transfer organizations between service providers
- **Charging plans**: Manage billing configuration and charging plans
- **Group management**: Handle user groups and permission sharing
- **Status management**: Control account and phone service status

### Available Tools Summary

#### Entity

- `add`: Add an entity (users, organizations, service providers) based on the provided parameters
- `get`: Retrieve entities based on the provided parameters
- `edit`: Edit an entity (users, organizations, service providers) based on the provided parameters
- `delete`: Delete a user, organization, or service provider by ID or identifier
- `get-details`: Retrieve entity details by ID or identifier
- `get-user-groups`: Retrieve a list of group IDs for a user by ID or identifier
- `move-organization`: Move an organization to a specific service provider
- `set-control-panel-access`: Set control panel access for a user, organization, or service provider by ID or identifier
- `set-status`: Set the status for a user, organization, or service provider by ID or identifier
- `set-permissions-limits`: Set permissions and limits for an entity (users, organizations, service providers) by ID or identifier
- `get-permissions-limits`: Retrieve permissions and limits for an entity by ID or identifier
- `update-permissions-limits`: Update permissions and limits for an entity (users, organizations, service providers) by ID or identifier

#### Billing

- `get-charging-plans`: Retrieve charging plans
- `get-charging-packages`: Retrieve charging packages
- `get-charging-plan-details`: Retrieve charging plan details
- `get-destination-exceptions`: Retrieve destination exceptions
- `get-recharges`: Retrieve recharges

#### Extension

- `add-extension`: Add an extension to an entity (users, organizations, service providers) based on the provided parameters
- `get-extensions`: Retrieve all extensions based on the provided parameters
- `delete-extension`: Delete the extension for the provided extended number
- `get-provision-file`: Retrieve the provision file for the provided extended number
- `get-queue-agents`: Retrieve the agents for the provided queue
- `get-queue-membership`: Retrieve the membership for the provided queue
- `get-scheduled-conferences`: Retrieve the scheduled conferences for the provided extension
- `get-scheduled-conference-details`: Retrieve the scheduled conference details for the provided extension
- `get-auth-caller-id`: Retrieve the authorized caller ID by ID or by filter and extension
- `get-auth-caller-id-recharges`: Retrieve the recharge operations for an authorized caller ID
- `get-available-caller-id`: Retrieve available caller IDs for an extension
- `get-call-recording-settings`: Retrieve call recording settings for an extension
- `get-call-rules-in`: Retrieve inbound call rules for an extension
- `get-card-code`: Retrieve calling card details by ID, filter or extension
- `get-card-code-recharges`: Retrieve card code recharge operations
- `get-conference-settings`: Retrieve conference settings for an extension
- `get-extension-details`: Retrieve extension details by extended number
- `get-extension-settings`: Retrieve extension settings by extended number
- `get-fax-center-settings`: Retrieve fax center settings for an extension
- `get-scheduled-conference-sessions`: Retrieve scheduled conference sessions for an extension
- `get-sip-preferences`: Retrieve SIP preferences for an extension
- `get-voicemail-settings`: Retrieve voicemail settings for an extension

#### PBX

- `get-regions`: Retrieve regions for the provided country code
- `get-phone-languages`: Retrieve phone languages
- `get-interface-languages`: Retrieve interface languages
- `get-timezone`: Retrieve timezone
- `get-custom-alerts`: Retrieve custom alerts for the provided user ID or user identifier
- `get-custom-buttons`: Retrieve custom buttons for the provided user ID or user identifier
- `get-device-details`: Retrieve details for the provided device ID or serial
- `get-devices`: Retrieve devices for the provided owner ID, user ID, user identifier, assigned organization ID, or assigned extensions
- `get-equipment-list`: Retrieve equipment list
- `get-file-languages`: Retrieve file languages
- `get-folders`: Retrieve folders for the provided user ID or user identifier
- `get-owned-sounds`: Retrieve owned sounds for the provided user ID or user identifier
- `get-schema-versions`: Retrieve schema versions
- `get-shared-sounds`: Retrieve shared sounds for the provided user ID or user identifier
- `get-templates`: Retrieve templates for the provided user ID or user identifier
- `get-time-interval-blocks`: Retrieve time interval blocks for the provided user ID or user identifier
- `get-time-intervals`: Retrieve time intervals for the provided time interval block ID

#### Report

- `call-costs`: Retrieve call costs for a user
- `call-report`: Retrieve detailed call records for a user
- `quick-stats`: Retrieve quick stats for an account

#### Channel

- `get-channels`: Retrieve channels
- `get-codecs`: Retrieve codecs
- `get-public-no`: Retrieve public no
- `get-public-no-poll`: Retrieve public no poll
- `get-call-rules-out`: Retrieve call rules out
- `get-call-rules-out-group`: Retrieve call rules out group
- `get-channel-group-poll`: Retrieve channel group poll
- `get-channel-groups`: Retrieve channel groups

---

## Setup

### Requirements

| Component   | Minimum Version | Purpose                                                |
| ----------- | --------------- | ------------------------------------------------------ |
| **uv**      | Latest          | Python package manager (installs Python automatically) |
| **VoipNow** | `5.6+`          | VoipNow platform API integration                       |

**Supported operating systems:**

**Supported Operating Systems:**

<details>
<summary>Redhat OS</summary>

##### uv

```bash
pip install uv
```

uv also provides a standalone installer to download and install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

<details>
<summary>Debian OS</summary>

Minimal OS versions:

- Debian:
  - 12 ( Bookworm)
- Ubuntu:
  - 22.04 LTS

##### uv

```bash
pip install uv
```
uv also provides a standalone installer to download and install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary> macOS </summary>

##### uv

```bash
brew install uv
```
uv also provides a standalone installer to download and install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
</details>

<details>
<summary> Windows </summary>

##### uv
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
</details>


### Installation

**Quick setup:**

Get VoipNow Provisioning MCP running and verified quickly.

**Install and prepare**
```bash
# 1. Clone the repository
git clone <repository-url>

# 2. Navigate to VoipNow Provisioning directory
cd provisioning

# 3. Install dependencies
uv sync
```

### Quick Start

1. **Create a minimal config.json**

```json
{
  "appId": "your-app-id",
  "appSecret": "your-app-secret",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/abs/path/to/provisioning/.access_token",
  "logLevel": "info",
  "insecure": false
}
```

2. **Verify with MCP Inspector (STDIO)**

```bash
npx @modelcontextprotocol/inspector
```
> `Note:` To run MCP Inspector, Node.js 22.7.5 or higher is required. Using Node 20 or lower will cause installation/runtime errors.
- In Inspector, choose STDIO and set:
  - Command: `uv`
  - Args: `["--directory", "/abs/path/to/provisioning", "run", "src/main.py", "--config", "/abs/path/to/config.json"]`
  - Connect, then click `List Tools` to confirm discovery.

**Notes:**

- To run over HTTP later, start with: `uv run src/main.py --transport streamable-http --port 8000 --config /abs/path/to/config.json` and connect to `http://SERVER_IP:8000/mcp`. For secured HTTP, add `--secure` and set `authTokenMCP` in `config.json`, then connect with `Authorization: Bearer YOUR_AUTH_TOKEN`.

### Command-Line Arguments

The server supports the following command-line arguments:

| Argument          | Short | Default     | Description                                       |
| ----------------- | ----- | ----------- | ------------------------------------------------- |
| `--transport`     | `-t`  | `stdio`     | Transport type: `stdio`, `sse`, `streamable-http` |
| `--port`          | `-p`  | `8000`      | Port number for HTTP transports                   |
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

| Parameter          | Required | Description                                                                                                                                                                              |
| ------------------ | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `appId`            | yes      | Application ID from VoipNow App registration                                                                                                                                             |
| `appSecret`        | yes      | Application secret from VoipNow App registration                                                                                                                                         |
| `voipnowHost`      | yes      | VoipNow server URL (e.g., `https://your-voipnow-host.com`)                                                                                                                                    |
| `voipnowTokenFile` | yes      | File path to store/read access token                                                                                                                                                     |
| `authTokenMCP`     | depends  | Auth token for MCP (required when `--secure` is used)                                                                                                                                    |
| `logLevel`         | no       | Logging level: `debug`, `info`, `warning`, `error`                                                                                                                                       |
| `insecure`         | no       | `false` (default): Enables SSL certificate verification (recommended for production); `true`: Disables SSL certificate verification (use only for testing with self-signed certificates) |

**Security note:** Only set `insecure: true` when connecting to development or testing environments with self-signed certificates. Always use `insecure: false` (or omit the field) in production environments.

> [!NOTE]
> **Auto-reload**: The server reloads its configuration automatically whenever `config.json` or the token file is modified.

**Basic usage:**

```bash
# STDIO transport (local development)
uv run src/main.py --config /path/to/config.json

# HTTP transport (remote access)
uv run src/main.py --transport streamable-http --address 0.0.0.0 --port 8000 --config /path/to/config.json

# Enable authorization for HTTP transport
uv run src/main.py --transport streamable-http --address 0.0.0.0 --port 8000 --secure --config /path/to/config.json
```

> [!CAUTION]
> **TLS certificates**: This server does not allow bypassing TLS verification. Make sure your `voipnowHost` is configured with a valid certificate. For development with self-signed instances, you can terminate TLS through a trusted proxy or add the CA to your system trust store. Do not disable TLS verification globally.


---

## Configuration

This section explains how to set up VoipNow API credentials and configuring the MCP server for best performance.

### VoipNow App Credentials

#### Step 1: VoipNow App Registration

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
     - This allows the app to use only App Key and App Secret.
     - No additional user authentication is required.

3. **Save credentials**
   - Go to `App Registration` and locate your newly created app.
   - Record the following credentials:
     - `App ID/key`
     - `App secret`

> [!TIP]
> For detailed app registration instructions, see the [VoipNow Integration Guide](https://red.4psa.me/doc/hg/manual-integration/5.6.0/Register-App).

#### Step 2: Server Configuration

**Create configuration file:**

Navigate to your VoipNow Provisioning MCP server directory and create/update `config.json`:

```json
{
  "appId": "your-app-id-here",
  "appSecret": "your-app-secret-here",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/path/to/provisioning/.access_token",
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
  "voipnowTokenFile": "/home/user/mcp/provisioning/.access_token",
  "authTokenMCP": "KoMMbqUHaYXtBxh7XuJF09SZs",
  "logLevel": "info",
  "insecure": false
}
```

#### Step 3: Token Management

**Automatic token generation:**

Start the server (any transport) to automatically generate the initial access token:

```bash
# The server will create the token file if it doesn't exist
# Example: HTTP (Streamable HTTP)
uv run src/main.py --transport streamable-http --address 0.0.0.0 --port 8000 --config /path/to/config.json

# Example: STDIO
uv run src/main.py --config /path/to/config.json
```

To generate a new token:

- Every 5 minutes, the VoipNow Provisioning MCP server verifies whether the token is nearing expiration and generates a new one.

**Token file format:**

The token file specified by `voipnowTokenFile` is a plain-text line containing three fields, separated by colons, with values expressed in seconds:

```
<createdAtS>:<expiresAtS>:<accessToken>
```

Example:

```
1717081337:1717082237:eyJhbGciOi...
```

**Configuration change detection:**

The server monitors authentication-related settings (`appId`, `appSecret`, or `voipnowHost`). When any of these change, it automatically deletes the token file so a new one is generated with the updated configuration. This allows smooth transitions when switching VoipNow servers or updating credentials, without needing to manually remove the token file.

Do not modify this file manually. It is created and refreshed by the server.

### Container Support (Optional)

> [!NOTE]
> Container support is optional and only needed if you want to run the MCP server in a Docker/Podman container.

The VoipNow Provisioning MCP server supports containerization for isolated deployments and easier scaling.

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
   docker build -t voipnow-provisioning-mcp -f ./Containerfile .

   # Using Podman
   podman build -t voipnow-provisioning-mcp -f ./Containerfile .
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
     "logLevel": "info"
   }
   EOF
   ```

4. **Run container**

   ```bash
   # Using Docker
   docker run -d \
     --name voipnow-provisioning \
     -v $(pwd)/config.json:/app/config.json \
     -p 8000:8000 \
     voipnow-provisioning-mcp \
     -c /app/config.json -p 8000 -t streamable-http -a 0.0.0.0

   # Using Podman
   podman run -d \
     --name voipnow-provisioning \
     -v $(pwd)/config.json:/app/config.json:z \
     -p 8000:8000 \
     voipnow-provisioning-mcp \
     -c /app/config.json -p 8000 -t streamable-http -a 0.0.0.0
   ```

### MCP Transport Setup

Configure your MCP client to connect to the VoipNow Provisioning server using one of the supported transport methods.

#### STDIO Transport

> [!NOTE]
> STDIO transport runs the server as a child process - no network configuration needed.

**Configuration:**

```json
{
  "mcpServers": {
    "mcp-voipnow-provisioning": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/provisioning",
        "run",
        "src/main.py",
        "--config",
        "/path/to/config.json"
      ]
    }
  }
}
```

**Placeholders to replace:**

- `/path/to/provisioning` - The absolute path to the VoipNow Provisioning MCP server directory
- `/path/to/config.json` - The absolute path to your configuration file

#### HTTP Transports

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

The VoipNow Provisioning MCP server must be started before you begin to configure the MCP client.

**Start server:**

```bash
uv run src/main.py --transport streamable-http --port 8000 --secure --config /path/to/config.json
```

**Client configuration:**

```json
{
  "mcpServers": {
    "voipnow-provisioning": {
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
- `PORT` - The port number on which the MCP server is listening (default: 8000)
- `YOUR_AUTH_TOKEN` - The authentication token generated for security

##### SSE (Legacy)

> [!WARNING]
> SSE transport is deprecated. Use Streamable HTTP for new deployments.

The VoipNow Provisioning MCP server must be started before you begin to configure the MCP client.

**Start server:**

```bash
uv run src/main.py --transport sse --port 8000 --secure --config /path/to/config.json
```

**Client configuration:**

```json
{
  "mcpServers": {
    "voipnow-provisioning": {
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
- `PORT` - The port number on which the MCP server is listening (default: 8000)
- `YOUR_AUTH_TOKEN` - The authentication token generated for security

#### MCP Bundles (.mcpb)

To create a `.mcpb` file, you must first install the `mcpb` command:

```bash
npm install -g @anthropic-ai/mcpb
```

Since the `manifest.json` file is already created, go to root folder of the VoipNow Provisioning MCP server and run:

```bash
mcpb pack
```

The command creates a `.mcpb` file, which can be used in `Claude Desktop` app. The `config.json` file must now be located on the same machine where `Claude Desktop` is running, and the path must be provided in `Extension` windows.

---

## Tools Reference

### Entity

#### Add

- **Tool Name**: `add`
- **Description**: Add entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User).
- **Input Schema**:

| Parameter              | Type    | Description                                                                                                                                                   |
| ---------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| type                   | enum    | The type of entity to add ("User", "Organization", "ServiceProvider")                                                                                         |
| login                  | string  | The login for the entity                                                                                                                                      |
| firstName              | string  | The first name for the entity                                                                                                                                 |
| lastName               | string  | The last name for the entity                                                                                                                                  |
| company                | string  | The company for the entity                                                                                                                                    |
| email                  | string  | The email for the entity                                                                                                                                      |
| passwordAuto           | boolean | The password auto generation for the entity (default: false)                                                                                                  |
| password               | string  | The password for the entity                                                                                                                                   |
| forceUpdate            | boolean | The force update for entity on duplicate login (new login computed) (default: false)                                                                          |
| phone                  | string  | The phone number for the entity                                                                                                                               |
| fax                    | string  | The fax number for the entity                                                                                                                                 |
| address                | string  | The address for the entity                                                                                                                                    |
| city                   | string  | The city for the entity                                                                                                                                       |
| pcode                  | string  | The postal code for the entity                                                                                                                                |
| country                | string  | The country for the entity                                                                                                                                    |
| region                 | integer | The region for the entity. Use PBX:GetRegions method for the list of all available regions                                                                    |
| timezone               | integer | The timezone for the entity. Use PBX:GetTimezone method for the list of all available timezones                                                               |
| interfaceLang          | string  | The interface language for the entity                                                                                                                         |
| notes                  | string  | The notes for the entity                                                                                                                                      |
| serverID               | string  | Set CTRLPANEL to filter only account added from VoipNow control panel                                                                                         |
| chargingIdentifier     | string  | The charging identifier for the entity                                                                                                                        |
| subscriptionID         | string  | The subscription ID for the entity which is attached to the account                                                                                           |
| phoneLang              | string  | The language for the phone number for the user                                                                                                                |
| channelRuleID          | integer | Outgoing routing rules group ID for the user                                                                                                                  |
| role                   | enum    | The role for the user ("member", "administrator", "owner") (default: "member")                                                                                |
| templateID             | integer | Account template ID                                                                                                                                           |
| parentID***            | integer | The owner ID for the entity                                                                                                                                   |
| parentIdentifier***    | string  | The owner identifier for the entity                                                                                                                           |
| parentLogin***         | string  | The owner login for the entity                                                                                                                                |
| fromUser**             | string  | Context user ID for requests made on behalf of this user                                                                                                      |
| fromUserIdentifier**   | string  | Context user identifier for requests made on behalf of this user                                                                                              |
| chargingPlanID*        | integer | The charging plan ID for the entity                                                                                                                           |
| chargingPlanIdentifier*| string  | The charging plan identifier for the entity                                                                                                                   |
| verbose                | boolean | Response verbosity. Set 1 to receive detailed information on newly created account (default: false)                                                           |
| notifyOnly             | string  | Mask of 4 bits to setup notification preferences ASPOU (ADMIN{0/1}, SERVICE_PROVIDER{0/1}, ORGANIZATION{0/1}, USER{0/1})                                      |
| otherNotifyEmail       | string  | Additional notification email for the entity. The email address to which notifications are sent when a new account is created; typically used for automation. |
| dku                    | string  | Deployment keeping unit for the entity                                                                                                                        |
| accountFlag            | enum    | Account flag. Possible values: noneditablelogin                                                                                                               |
| identifier             | string  | The identifier for the entity                                                                                                                                 |
| linkResourceID         | integer | Linkage resource identifier (default: 1)                                                                                                                      |
| linkUUID               | string  | Remote linkage user identifier                                                                                                                                |

**Legend:**

- `*` - one of the fields should be provided, not both
- `**` - one of the fields should be provided, not both (for `User` and `Organization`)
- `***` - one of the fields should be provided, not all (for `User` and `Organization`, except `parentLogin` for `ServiceProvider`)

#### Get

- **Tool Name**: `get`
- **Description**: Retrieve entities (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Use parentID to filter.
- **Input Schema**:

| Parameter        | Type    | Description                                                                                     |
| ---------------- | ------- | ----------------------------------------------------------------------------------------------- |
| type             | enum    | The type of entity to retrieve for ("User", "Organization", "ServiceProvider")                  |
| templateID       | integer | Account template ID                                                                             |
| serverID         | string  | Set CTRLPANEL to filter only accounts added from VoipNow control panel                          |
| filter           | string  | Filter list ("name","company","email","login")                                                  |
| parentID*        | integer | Owner ID                                                                                        |
| parentIdentifier*| string  | Unique owner identifier                                                                         |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Edit

- **Tool Name**: `edit`
- **Description**: Edit entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Specify entity with ID or identifier.
- **Input Schema**:

| Parameter              | Type    | Description                                                                                     |
| ---------------------- | ------- | ----------------------------------------------------------------------------------------------- |
| type                   | enum    | The type of entity to add ("User", "Organization", "ServiceProvider")                           |
| login                  | string  | The login for the entity                                                                        |
| firstName              | string  | The first name for the entity                                                                   |
| lastName               | string  | The last name for the entity                                                                    |
| company                | string  | The company for the entity                                                                      |
| email                  | string  | The email for the entity                                                                        |
| passwordAuto           | boolean | The password auto generation for the entity (default: false)                                    |
| password               | string  | The password for the entity                                                                     |
| forceUpdate            | boolean | The force update for entity on duplicate login (new login computed) (default: false)            |
| phone                  | string  | The phone number for the entity                                                                 |
| fax                    | string  | The fax number for the entity                                                                   |
| address                | string  | The address for the entity                                                                      |
| city                   | string  | The city for the entity                                                                         |
| pcode                  | string  | The postal code for the entity                                                                  |
| country                | string  | The country for the entity                                                                      |
| region                 | integer | The region for the entity. Use PBX:GetRegions method for the list of all available regions      |
| timezone               | integer | The timezone for the entity. Use PBX:GetTimezone method for the list of all available timezones |
| interfaceLang          | string  | The interface language for the entity                                                           |
| notes                  | string  | The notes for the entity                                                                        |
| serverID               | string  | Set CTRLPANEL to filter only account added from VoipNow control panel                           |
| chargingIdentifier     | string  | The charging identifier for the entity                                                          |
| subscriptionID         | string  | The subscription ID for the entity which is attached to the account                             |
| phoneLang              | string  | The language for the phone number for the user                                                  |
| channelRuleID          | integer | Outgoing routing rules group ID for the user                                                    |
| role                   | enum    | The role for the user ("member", "administrator", "owner") (default: "member")                  |
| templateID             | integer | Account template ID                                                                             |
| fromUser**             | string  | Context user ID for requests made on behalf of this user                                        |
| fromUserIdentifier**   | string  | Context user identifier for requests made on behalf of this user                                |
| chargingPlanID*        | integer | The charging plan ID for the entity                                                             |
| chargingPlanIdentifier*| string  | The charging plan identifier for the entity                                                     |
| ID*                    | integer | The ID for the entity                                                                           |
| identifier*            | string  | The identifier for the entity                                                                   |

**Legend:**

- `*` - one of the fields should be provided, not both
- `**` - one of the fields should be provided, not both (for `User` and `Organization`)

#### Delete

- **Tool Name**: `delete`
- **Description**: Delete entity (users, organizations, service providers). Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). WARNING: Deleting higher-level entities cascades to children.
- **Input Schema**:

| Parameter  | Type    | Description                                                                            |
| ---------- | ------- | -------------------------------------------------------------------------------------- |
| type       | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider") |
| ID*        | array   | The IDs for the entities to delete                                                     |
| identifier*| array   | The unique identifiers for entities to delete                                          |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Details

- **Tool Name**: `get-details`
- **Description**: Retrieve entity details by ID or identifier.
- **Input Schema**:

| Parameter  | Type    | Description                                                                            |
| ---------- | ------- | -------------------------------------------------------------------------------------- |
| type       | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider") |
| ID*        | integer | The ID for the entity                                                                  |
| identifier*| string  | The unique identifier for the entity                                                   |

**Legend:**

- `*` - one of the field should be provided, not both

#### Get User Groups

- **Tool Name**: `get-user-groups`
- **Description**: Retrieve a list of group IDs for the user by ID or by identifier.
- **Input Schema**:

| Parameter  | Type    | Description                                         |
| ---------- | ------- | --------------------------------------------------- |
| type       | enum    | The type of entity to retrieve details for ("User") |
| ID*        | integer | The ID for the entity                               |
| identifier*| string  | The unique identifier for the entity                |
| share      | boolean | Groups that this extension can share info with      |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Move Organization

- **Tool Name**: `move-organization`
- **Description**: Move organization to a specific service provider.
- **Input Schema**:

| Parameter                 | Type    | Description                                                 |
| ------------------------- | ------- | ----------------------------------------------------------- |
| type                      | enum    | The type of entity to retrieve details for ("Organization") |
| ID*                       | array   | The IDs for the entities to move                            |
| identifier*               | array   | The unique identifiers for the entities to move             |
| serviceProviderID*        | integer | The ID for the service provider                             |
| serviceProviderIdentifier*| string  | The unique identifier for the service provider              |
| chargingPlanID*           | integer | The ID for the charging plan                                |
| chargingPlanIdentifier*   | string  | The unique identifier for the charging plan                 |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Set Control Panel Access

- **Tool Name**: `set-control-panel-access`
- **Description**: Set control panel access for a user, organization or service provider by ID or identifier.
  - `cpAccess`=`false` entity panel access is `DISABLED`
  - `cpAccess`=`true` entity panel access is `ENABLED`
- **Input Schema**:

| Parameter  | Type    | Description                                                                            |
| ---------- | ------- | -------------------------------------------------------------------------------------- |
| type       | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider") |
| cpAccess   | boolean | The control panel access for the entity                                                |
| ID*        | integer | The ID for the entity                                                                  |
| identifier*| string  | The unique identifier for the entity                                                   |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Set Status

- **Tool Name**: `set-status`
- **Description**: Set status for a user, organization or service provider by ID or identifier.
  - `status`=`false` entity account is `DISABLED`
  - `status`=`true` entity account is `ENABLED`
- **Input Schema**:

| Parameter   | Type    | Description                                                                                     |
| ----------- | ------- | ----------------------------------------------------------------------------------------------- |
| type        | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider")          |
| status      | boolean | The status for the entity                                                                       |
| phoneStatus | enum    | The phone status for the entity ("1","16","32","64")                                            |
| ID*         | integer | The ID for the entity                                                                           |
| identifier* | string  | The unique identifier for the entity                                                            |

**Legend:**

- `*` - one of the fields should be provided, not both

**phoneStatus Values:**

- 1: Customer can dial out and receive calls
- 16: Customer can be called and can call internally
- 32: Customer can only be called
- 64: Customer can not use phone service

#### Set Permissions and Limits

- **Tool Name**: `set-permissions-limits`
- **Description**: Set permissions and limits for entity (users, organizations, service providers) by ID or identifier.
- **Input Schema**:

| Parameter              | Type    | Description                                                                                                                                     |
| ---------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| type                   | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider")                                                          |
| ID*                    | integer | The ID for the entity                                                                                                                           |
| identifier*            | string  | The unique identifier for the entity                                                                                                            |
| extensionManag         | boolean | Enable extension and user management                                                                                                            |
| extFeatureManag        | boolean | Enable extension features management                                                                                                            |
| sipManag               | boolean | Enable Phone extension SIP management                                                                                                           |
| sipTrunkingManag       | boolean | Enable SIP trunking management                                                                                                                  |
| soundManag             | boolean | Enable sound management                                                                                                                         |
| numberManag            | boolean | Enable Phone numbers management                                                                                                                 |
| callAPIManag           | boolean | Enable UnifiedAPI management                                                                                                                    |
| callerIDManag          | boolean | Enable CallerID management                                                                                                                      |
| provisionManag         | enum    | Enable Provision device management ("0", "2", "4") (default: "0")                                                                               |
| accountExpire*         | string  | Account expiration date; date format should be (YYYY-MM-DD) or 'unlimited' for no expiration (default: "unlimited")                             |
| accountExpireDays*     | string  | Account expiration number of days, counted from setup; should be a number or 'unlimited' for no expiration (default: "unlimited")               |
| phoneExtMax            | string  | The maximum number of phone terminal extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")           |
| queueExtMax            | string  | The maximum number of queue extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                    |
| ivrExtMax              | string  | The maximum number of IVR extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                      |
| voicemailExtMax        | string  | The maximum number of voicemail center extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")         |
| queuecenterExtMax      | string  | The maximum number of queue login center extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")       |
| confExtMax             | string  | The maximum number of conference extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")               |
| callbackExtMax         | string  | The maximum number of callback extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                 |
| callbackCallerIDMax    | string  | The maximum number of callback caller IDs for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                 |
| callCardExtMax         | string  | The maximum number of call card extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                |
| callCardCodesMax       | string  | The maximum number of call card codes for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                     |
| intercomExtMax         | string  | The maximum number of intercom/paging extensions for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")          |
| concurentCalls         | string  | The maximum number of public concurrent calls for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")             |
| concurentInternalCalls | string  | The maximum number of internal concurrent calls for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")           |
| queueMembersMax        | string  | The maximum number of queue members for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                       |
| mailboxMax             | string  | The maximum number of mailboxes for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                           |
| storage                | string  | The maximum amount of storage (MB) for the entity; should be a number or 'unlimited' for no limit (default: "unlimited")                        |
| multiUser              | boolean | Multi-user aware property for User entity                                                                                                       |
| shareVoicemail         | string  | Share voicemail messages with other users for User entity; should be a groupID or 'everybody' for no restriction                                |
| shareFaxes             | string  | Share faxes messages with other users for User entity; should be a groupID or 'everybody' for no restriction                                    |
| shareRecordings        | string  | Share recordings messages with other users for User entity; should be a groupID or 'everybody' for no restriction                               |
| shareCallHistory       | string  | Share call history messages with other users for User entity; should be a groupID or 'everybody' for no restriction                             |
| permsManag             | boolean | Enable role management for Organization/Service Provider entity                                                                                 |
| chargingPlanManag      | boolean | Enable charging plan management for Organization/Service Provider entity                                                                        |
| userMax                | string  | The maximum number of users for the Organization/Service Provider entity; should be a number or 'unlimited' for no limit (default: "unlimited") |
| organizationType       | enum    | The type of the Organization entity; should be 0 for Business, 1 for Residential group (default: "0")                                           |
| organizationManag      | boolean | Enable organization management for ServiceProvider entity                                                                                       |
| stackedManag           | boolean | Enable See stacked phone numbers for ServiceProvider entity                                                                                     |
| organizationMax        | string  | The maximum number of organizations for the ServiceProvider entity; should be a number or 'unlimited' for no limit (default: "unlimited")       |

**Legend:**

- `*` - one of the fields should be provided, not both

**provisionManag Values:**

- 0: None
- 2: View
- 4: Modify

#### Get Permissions and Limits

- **Tool Name**: `get-permissions-limits`
- **Description**: Retrieve permissions and limits for the entity by ID or identifier.
- **Input Schema**:

| Parameter  | Type    | Description                                                                            |
| ---------- | ------- | -------------------------------------------------------------------------------------- |
| type       | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider") |
| ID*        | integer | The ID for the entity                                                                  |
| identifier*| string  | The unique identifier for the entity                                                   |

**Legend:**

- `*` - one of the field should be provided, not both

#### Update Permissions and Limits

- **Tool Name**: `update-permissions-limits`
- **Description**: Update permissions and limits for the entity (users, organizations, service providers) by ID or identifier.
- **Input Schema**:

| Parameter              | Type    | Description                                                                                                                      |
| ---------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------- |
| type                   | enum    | The type of entity to retrieve details for ("User", "Organization", "ServiceProvider")                                           |
| operation              | enum    | Available options for UpdateUserPL, UpdateOrganizationPL, UpdateServiceProviderPL ("increase", "decrease", "unlimited", "value") |
| ID*                    | integer | The ID for the entity                                                                                                            |
| identifier*            | string  | The unique identifier for the entity                                                                                             |
| extensionManag         | boolean | Enable extension and user management                                                                                             |
| extFeatureManag        | boolean | Enable extension features management                                                                                             |
| sipManag               | boolean | Enable Phone extension SIP management                                                                                            |
| sipTrunkingManag       | boolean | Enable SIP trunking management                                                                                                   |
| soundManag             | boolean | Enable sound management                                                                                                          |
| numberManag            | boolean | Enable Phone numbers management                                                                                                  |
| callAPIManag           | boolean | Enable UnifiedAPI management                                                                                                     |
| callerIDManag          | boolean | Enable CallerID management                                                                                                       |
| provisionManag         | enum    | Enable Provision device management ("0", "2", "4") (default: "0")                                                                |
| accountExpire          | string  | Account expiration date; date format should be (YYYY-MM-DD) or 'unlimited' for no expiration (default: "unlimited")              |
| accountExpireDays      | string  | Account expiration number of days, counted from setup; should be a number or 'unlimited' for no expiration                       |
| phoneExtMax            | string  | The maximum number of phone terminal extensions for the entity; should be a number                                               |
| queueExtMax            | string  | The maximum number of queue extensions for the entity; should be a number                                                        |
| ivrExtMax              | string  | The maximum number of IVR extensions for the entity; should be a number                                                          |
| voicemailExtMax        | string  | The maximum number of voicemail center extensions for the entity; should be a number                                             |
| queuecenterExtMax      | string  | The maximum number of queue login center extensions for the entity; should be a number                                           |
| confExtMax             | string  | The maximum number of conference extensions for the entity; should be a number                                                   |
| callbackExtMax         | string  | The maximum number of callback extensions for the entity; should be a number                                                     |
| callbackCallerIDMax    | string  | The maximum number of callback caller IDs for the entity; should be a number                                                     |
| callCardExtMax         | string  | The maximum number of call card extensions for the entity; should be a number                                                    |
| callCardCodesMax       | string  | The maximum number of call card codes for the entity; should be a number                                                         |
| intercomExtMax         | string  | The maximum number of intercom/paging extensions for the entity; should be a number                                              |
| concurentCalls         | string  | The maximum number of public concurrent calls for the entity; should be a number                                                 |
| concurentInternalCalls | string  | The maximum number of internal concurrent calls for the entity; should be a number                                               |
| queueMembersMax        | string  | The maximum number of queue members for the entity; should be a number                                                           |
| mailboxMax             | string  | The maximum number of mailboxes for the entity; should be a number                                                               |
| storage                | string  | The maximum amount of storage (MB) for the entity; should be a number                                                            |
| multiUser              | boolean | Multi-user aware property for User entity                                                                                        |
| permsManag             | boolean | Enable roles management for Organization/Service Provider entity                                                                 |
| chargingPlanManag      | boolean | Enable charging plan management for Organization/Service Provider entity                                                         |
| userMax                | string  | The maximum number of users for the Organization/Service Provider entity; should be a number                                     |
| organizationManag      | boolean | Enable organization management for ServiceProvider entity                                                                        |
| stackedManag           | boolean | Enable See stacked phone numbers for ServiceProvider entity                                                                      |
| organizationMax        | string  | The maximum number of organizations for the ServiceProvider entity; should be a number                                           |

**Legend:**

- `*` - one of the fields should be provided, not both

**provisionManag Values:**

- 0: None
- 2: View
- 4: Modify

### Billing

#### Get Charging Plans

- **Tool Name**: `get-charging-plans`
- **Description**: Retrieve charging plans.
- **Input Schema**:

| Parameter      | Type    | Description                                                                                     |
| -------------- | ------- | ----------------------------------------------------------------------------------------------- |
| userID*        | integer | The ID for the account                                                                          |
| userIdentifier*| string  | The unique identifier for the account                                                           |
| filter         | string  | The filter for the entity ("name", "company", "email", "login")                                 |
| default        | boolean | Set to filter default charging plan                                                             |

**Legend:**

- `*` - one of the field should be provided, not both

#### Get Charging Packages

- **Tool Name**: `get-charging-packages`
- **Description**: Retrieve charging packages.
- **Input Schema**:

| Parameter      | Type    | Description                    |
| -------------- | ------- | ------------------------------ |
| chargingPlanID | integer | The ID for the charging plan   |

#### Get Charging Plan Details

- **Tool Name**: `get-charging-plan-details`
- **Description**: Retrieve charging plan details.
- **Input Schema**:

| Parameter   | Type    | Description                               |
| ----------- | ------- | ----------------------------------------- |
| ID*         | integer | The ID for the charging plan               |
| identifier* | string  | The unique identifier for the charging plan |

**Legend:**

- `*` - one of the field should be provided, not both

#### Get Destination Exceptions

- **Tool Name**: `get-destination-exceptions`
- **Description**: Retrieve destination exceptions.
- **Input Schema**:

| Parameter      | Type    | Description                                                           |
| -------------- | ------- | --------------------------------------------------------------------- |
| chargingPlanID | integer | The ID for the charging plan                                          |
| filter         | string  | Filter destination exception charges list after areaCode, description |

#### Get Recharges

- **Tool Name**: `get-recharges`
- **Description**: Retrieve recharges.
- **Input Schema**:

| Parameter       | Type    | Description                      |
| ----------------| ------- | -------------------------------- |
| userID*         | integer | The ID for the account           |
| userIdentifier* | string  | The unique identifier for the account |

**Legend:**

- `*` - one of the fields should be provided, not both

### Extension

#### Add Extension

- **Tool Name**: `add-extension`
- **Description**: Add extension to a User. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Extensions belong to Users (parentID = User ID).
- **Input Schema**:

| Parameter          | Type    | Description                                                                                                                                    |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| extensionNo        | string  | The extension number to add                                                                                                                    |
| templateID         | integer | The ID for the template                                                                                                                        |
| extensionType      | enum    | The type of extension to add ("term", "phoneQueue", "ivr", "voicecenter", "conference", "callback", "callcard", "intercom", "queuecenter")     |
| label              | string  | The label for the extension                                                                                                                    |
| password           | string  | The password for the extension                                                                                                                 |
| passwordAuto       | boolean | The password auto generation for the entity (default: false)                                                                                   |
| forceUpdate        | boolean | The force update for entity on duplicate login (new login computed) (default: false)                                                           |
| parentID*          | integer | The ID for the parent entity                                                                                                                   |
| parentIdentifier*  | string  | The identifier for the parent entity                                                                                                           |
| parentLogin*       | string  | The login for the parent entity                                                                                                                |
| fromUser*          | string  | The from user for the extension                                                                                                                |
| fromUserIdentifier*| string  | The from user identifier for the extension                                                                                                     |
| verbose            | boolean | Response verbosity. Set 1 to receive detailed information on newly created account (default: false)                                            |
| notifyOnly         | string  | Mask of 4 bits to setup notification preferences ASPOU (ADMIN{0/1}, SERVICE_PROVIDER{0/1}, ORGANIZATION{0/1}, USER{0/1})                       |
| otherNotifyEmail   | string  | Additional notification email for the entity. The email address where to send email when a new account is created; usually used in automation. |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Extensions

- **Tool Name**: `get-extensions`
- **Description**: Retrieve extensions. Hierarchy: Admin -> ServiceProvider (parent=Admin) -> Organization (parent=ServiceProvider) -> User (parent=Organization) -> Extension (parent=User). Filter by User with parentID.
- **Input Schema**:

| Parameter        | Type    | Description                                                                                                                                     |
| ---------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| extensionType    | enum    | The type of extension to retrieve ("term", "phoneQueue", "ivr", "voicecenter", "conference", "callback", "callcard", "intercom", "queuecenter") |
| templateID       | integer | The ID for the template                                                                                                                         |
| filter           | string  | The filter for the entity ("name", "company", "email", "login")                                                                                 |
| parentID*        | integer | Owner ID                                                                                                                                        |
| parentIdentifier*| string  | Unique owner identifier                                                                                                                         |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Delete Extension

- **Tool Name**: `delete-extension`
- **Description**: Delete the extension for the provided extended number.
- **Input Schema**:

| Parameter        | Type    | Description                                         |
| ---------------- | ------- | --------------------------------------------------- |
| extendedNumber   | array   | A list of extension extended numbers to be deleted. |

#### Get Provision File

- **Tool Name**: `get-provision-file`
- **Description**: Retrieve the provision file for the provided extended number
- **Input Schema**:

| Parameter       | Type  | Description                                           |
|-----------------|-------|-------------------------------------------------------|
| extendedNumber  | string| Extended number for which to retrieve the provision   |

#### Get Queue Agents

- **Tool Name**: `get-queue-agents`
- **Description**: Retrieve the agents for the provided queue
- **Input Schema**:

| Parameter       | Type   | Description                                                |
|-----------------|--------|------------------------------------------------------------|
| extendedNumber  | string | Queue extended number                                      |
| filter          | enum   | Agent location filter ("all", "local", "remote"). Default: "all" |

#### Get Queue Membership

- **Tool Name**: `get-queue-membership`
- **Description**: Retrieve the membership for the provided queue
- **Input Schema**:

| Parameter       | Type   | Description                               |
|-----------------|--------|-------------------------------------------|
| extendedNumber  | string | Queue extended number                      |

#### Get Scheduled Conferences

- **Tool Name**: `get-scheduled-conferences`
- **Description**: Retrieve the scheduled conferences for the provided extension
- **Input Schema**:

| Parameter         | Type   | Description            |
|-------------------|--------|------------------------|
| filter            | string | Filter string          |
| interval          | enum   | Time interval when the conferences were scheduled  |
| extendedNumber    | string | Extension number       |

#### Get Scheduled Conference Details

- **Tool Name**: `get-scheduled-conference-details`
- **Description**: Retrieve the scheduled conference details for the provided extension
- **Input Schema**:

| Parameter         | Type   | Description                                   |
|-------------------|--------|-----------------------------------------------|
| conferenceNumber  | string | Conference number                             |
| extendedNumber    | string | Extension extended number                     |

#### Get Auth Caller ID

- **Tool Name**: `get-auth-caller-id`
- **Description**: Retrieve the auth caller id for the provided extended number
- **Input Schema**:

| Parameter       | Type    | Description                                                                 |
|-----------------|---------|-----------------------------------------------------------------------------|
| ID*             | integer | CallerID record ID                                                          |
| filter**        | string  | Filter string                                                               |
| extendedNumber**| string  | Extension extended number                                                   |

**Legend:**

- `*` - exactly one of `ID` or the pair `filter`+`extendedNumber` must be provided
- `**` - must be provided together if `ID` is not provided

#### Get Auth Caller ID Recharges

- **Tool Name**: `get-auth-caller-id-recharges`
- **Description**: Retrieve the auth caller id recharges for the provided extended number
- **Input Schema**:

| Parameter | Type    | Description           |
|-----------|---------|-----------------------|
| ID        | integer | CallerID record ID    |

#### Get Available Caller ID

- **Tool Name**: `get-available-caller-id`
- **Description**: Retrieve the available caller id for the provided extended number
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Call Recording Settings

- **Tool Name**: `get-call-recording-settings`
- **Description**: Retrieve the call recording settings for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Call Rules In

- **Tool Name**: `get-call-rules-in`
- **Description**: Retrieve the inbound call rules for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Card Code

- **Tool Name**: `get-card-code`
- **Description**: Retrieve calling card details by ID, filter or extension
- **Input Schema**:

| Parameter       | Type    | Description                         |
|-----------------|---------|-------------------------------------|
| ID*             | integer | Card code ID                        |
| filter*         | string  | Filter string                        |
| extendedNumber* | string  | Extension extended number            |

**Legend:**

- `*` - exactly one of the fields should be provided

#### Get Card Code Recharges

- **Tool Name**: `get-card-code-recharges`
- **Description**: Retrieve recharge operations for a calling card
- **Input Schema**:

| Parameter | Type    | Description  |
|-----------|---------|--------------|
| ID        | integer | Card code ID |

#### Get Conference Settings

- **Tool Name**: `get-conference-settings`
- **Description**: Retrieve conference settings for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Extension Details

- **Tool Name**: `get-extension-details`
- **Description**: Retrieve details for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Extension Settings

- **Tool Name**: `get-extension-settings`
- **Description**: Retrieve settings for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Fax Center Settings

- **Tool Name**: `get-fax-center-settings`
- **Description**: Retrieve fax center settings for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Scheduled Conference Sessions

- **Tool Name**: `get-scheduled-conference-sessions`
- **Description**: Retrieve the scheduled conference sessions for the provided extension
- **Input Schema**:

| Parameter         | Type   | Description            |
|-------------------|--------|------------------------|
| started           | string | Start date (YYYY-MM-DD)|
| ended             | string | End date (YYYY-MM-DD)  |
| conferenceNumber  | string | Conference number      |
| extendedNumber    | string | Extension number       |

#### Get SIP Preferences

- **Tool Name**: `get-sip-preferences`
- **Description**: Retrieve SIP preferences for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

#### Get Voicemail Settings

- **Tool Name**: `get-voicemail-settings`
- **Description**: Retrieve voicemail settings for the provided extension
- **Input Schema**:

| Parameter      | Type   | Description                  |
|----------------|--------|------------------------------|
| extendedNumber | string | Extension extended number    |

### PBX

#### Get Regions

- **Tool Name**: `get-regions`
- **Description**: Retrieve regions for the provided code
- **Input Schema**:

| Parameter | Type   | Description                        |
|-----------|--------|------------------------------------|
| code      | string | Country code                       |
| region    | string | Region name to filter result       |

#### Get Phone Languages

- **Tool Name**: `get-phone-languages`
- **Description**: Retrieve phone languages.
- **Input Schema**: (No parameters required)

#### Get Interface Languages

- **Tool Name**: `get-interface-languages`
- **Description**: Retrieve interface languages.
- **Input Schema**: (No parameters required)

#### Get Timezone

- **Tool Name**: `get-timezone`
- **Description**: Retrieve timezone.
- **Input Schema**:

| Parameter | Type   | Description  |
|-----------|--------|--------------|
| code      | string | Country code |

#### Get Custom Alerts

- **Tool Name**: `get-custom-alerts`
- **Description**: Retrieve custom alerts for the provided user ID or user identifier.
- **Input Schema**:

| Parameter      | Type    | Description                                               |
|----------------|---------|-----------------------------------------------------------|
| userID*        | integer | Custom alert owner ID                                     |
| userIdentifier*| string  | Custom alert owner identifier                             |
| displayLevel   | enum    | Display level ("admin","reseller","client","extension"). Default: "admin" |
| filter         | string  | Filter custom alerts list by text                         |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Custom Buttons

- **Tool Name**: `get-custom-buttons`
- **Description**: Retrieve custom buttons for the provided user ID or user identifier.
- **Input Schema**:

| Parameter      | Type    | Description                          |
|----------------|---------|--------------------------------------|
| userID*        | integer | Custom alert owner ID                |
| userIdentifier*| string  | Custom alert owner identifier        |
| filter         | string  | Filter custom buttons list by text   |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Device Details

- **Tool Name**: `get-device-details`
- **Description**: Retrieve details for the provided device ID or serial.
- **Input Schema**:

| Parameter | Type    | Description           |
|-----------|---------|-----------------------|
| deviceID* | integer | The ID of the device  |
| serial*   | string  | Device serial         |

**Legend:**

- `*` - exactly one of the fields should be provided

#### Get Devices

- **Tool Name**: `get-devices`
- **Description**: Retrieve devices for the provided owner ID, user ID, user identifier, assigned organization ID, or assigned extensions.
- **Input Schema**:

| Parameter             | Type    | Description                                  |
|-----------------------|---------|----------------------------------------------|
| ownerID**             | integer | ID of the owner of the device                |
| userID**              | integer | Devices seen by user with this ID            |
| userIdentifier**      | string  | Devices seen by user with this identifier    |
| assignedOrganizationID| integer | ID of the client assigned to the device      |
| assignedExtensions    | array   | Extensions assigned to the device (integers) |

**Legend:**

- `**` - not both fields should be provided together

#### Get Equipment List

- **Tool Name**: `get-equipment-list`
- **Description**: Retrieve equipment list.
- **Input Schema**: (No parameters required)

#### Get File Languages

- **Tool Name**: `get-file-languages`
- **Description**: Retrieve file languages.
- **Input Schema**:

| Parameter | Type    | Description     |
|-----------|---------|-----------------|
| ID        | integer | Sound file id   |

#### Get Folders

- **Tool Name**: `get-folders`
- **Description**: Retrieve folders for the provided user ID or user identifier.
- **Input Schema**:

| Parameter      | Type    | Description                                                                 |
|----------------|---------|-----------------------------------------------------------------------------|
| userID*        | integer | User ID                                                                     |
| userIdentifier*| string  | User identifier                                                              |
| musicOnHold    | enum    | -1 all, 0 no MOH, 1 only MOH. Default: 0                                    |
| emptyFolder    | enum    | 0 all folders, 1 non-empty folders. Default: 0                              |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Owned Sounds

- **Tool Name**: `get-owned-sounds`
- **Description**: Retrieve owned sounds for the provided user ID or user identifier.
- **Input Schema**:

| Parameter      | Type    | Description                                                             |
|----------------|---------|-------------------------------------------------------------------------|
| userID*        | integer | User ID                                                                 |
| userIdentifier*| string  | User identifier                                                          |
| folderID       | integer | Set 0 for all folders                                                   |
| languageID     | integer | Set 0 for all files                                                     |
| musicOnHold    | enum    | -1 all files, 0 non MOH, 1 MOH. Default: -1                             |
| system         | enum    | -1 all files, 0 non system, 1 system. Default: -1                       |
| status         | integer | Status filter. Default: -1                                              |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Schema Versions

- **Tool Name**: `get-schema-versions`
- **Description**: Retrieve schema versions.
- **Input Schema**: (No parameters required)

#### Get Shared Sounds

- **Tool Name**: `get-shared-sounds`
- **Description**: Retrieve shared sounds for the provided user ID or user identifier.
- **Input Schema**:

| Parameter      | Type    | Description                                        |
|----------------|---------|----------------------------------------------------|
| userID*        | integer | User ID                                            |
| userIdentifier*| string  | User identifier                                     |
| own            | boolean | True to filter sounds created by the user. Default: true |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Templates

- **Tool Name**: `get-templates`
- **Description**: Retrieve templates for the provided user ID or user identifier.
- **Input Schema**:

| Parameter       | Type    | Description                                                                 |
|-----------------|---------|-----------------------------------------------------------------------------|
| ID              | integer | User template ID                                                            |
| userLevel       | enum    | "serviceProvider","organization","user","extension". Default: "term"         |
| extensionType   | enum    | "term","phoneQueue","ivr","voicecenter","conference","callback","callcard","intercom","queuecenter" |
| userID*         | integer | Template owner ID                                                           |
| userIdentifier* | string  | Template owner identifier                                                   |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Time Interval Blocks

- **Tool Name**: `get-time-interval-blocks`
- **Description**: Retrieve time intervals blocks for the provided user ID or user identifier
- **Input Schema**:

| Parameter      | Type    | Description                            |
|----------------|---------|----------------------------------------|
| filter         | string  | Filter time interval blocks by name    |
| userID*        | integer | Time interval owner ID                 |
| userIdentifier*| string  | Time interval owner identifier         |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Get Time Intervals

- **Tool Name**: `get-time-intervals`
- **Description**: Retrieve time intervals for the provided time interval block ID.
- **Input Schema**:

| Parameter | Type    | Description            |
|-----------|---------|------------------------|
| ID        | integer | Time interval block ID |

### Report

#### Call Costs

- **Tool Name**: `call-costs`
- **Description**: Retrieve call costs for a specific user
- **Input Schema**:

| Parameter       | Type    | Description                                               |
| ----------------| ------- | ----------------------------------------------------------|
| userID*         | integer | Account ID                                                |
| userIdentifier* | string  | Account identifier                                        |
| interval**      | object  | Search between startDate and endDate (YYYY-MM-DD)         |
| year**          | integer | Search year. Default: current year                        |
| month**         | integer | Search month. Default: current month                      |
| prepareDelete   | boolean | Set flag to mark client in state: irreversible suspension |

**Legend:**

- `*` - one of the fields should be provided, not both
- `**` - provide either `interval` or the pair `year`+`month`, not both

#### Call Report

- **Tool Name**: `call-report`
- **Description**: Retrieve call report for a specific user
- **Input Schema**:

| Parameter       | Type    | Description                                                                             |
| ----------------| ------- | --------------------------------------------------------------------------------------- |
| userID*         | integer | Account ID                                                                              |
| userIdentifier* | string  | Account identifier                                                                      |
| interval        | object  | Search between startDate and endDate (YYYY-MM-DD)                                       |
| flow            | enum    | Call flow ("in", "out")                                                                 |
| type            | enum    | Call type ("local", "elocal", "out")                                                    |
| disposition     | enum    | Call disposition ("ANSWERED", "BUSY", "FAILED", "NO ANSWER", "UNKNOWN", "NOT ALLOWED")  |
| records         | integer | Number of records to be returned. Maximum: 1,000. Default: 1000                         |
| hangupCause     | integer | Filter report by hangup cause                                                           |
| networkCode     | string  | Filter report by network code                                                           |

**Legend:**

- `*` - one of the fields should be provided, not both

#### Quick Stats

- **Tool Name**: `quick-stats`
- **Description**: Retrieve quick stats for a specific entity
- **Input Schema**:

| Parameter       | Type    | Description         |
| ----------------| ------- | ------------------- |
| userID*         | integer | Account ID          |
| userIdentifier* | string  | Account identifier  |
| login*          | string  | Account username    |

**Legend:**

- `*` - exactly one of the fields should be provided

### Channel

#### Get Channels

- **Tool Name**: `get-channels`
- **Description**: Retrieve channels.
- **Input Schema**:

| Parameter | Type    | Description                          |
|-----------|---------|--------------------------------------|
| groupID   | integer | Group ID                             |
| enabled   | boolean | Filter by enabled status              |
| flow      | enum    | Channel flow ("in", "out", "both") |
| filter    | string  | Filter string                         |

#### Get Codecs

- **Tool Name**: `get-codecs`
- **Description**: Retrieve codecs.
- **Input Schema**:

| Parameter | Type    | Description                |
|-----------|---------|----------------------------|
| channelID | integer | The ID for the channel     |

#### Get Public No

- **Tool Name**: `get-public-no`
- **Description**: Retrieve public no.
- **Input Schema**:

| Parameter       | Type    | Description                            |
|-----------------|---------|----------------------------------------|
| channelID       | integer | The ID for the channel                 |
| inUse           | boolean | Filter by in use (Default: false)      |
| type            | enum    | Number type ("exclusive", "stacked") |
| filter          | string  | Filter string                           |
| extendedNumber* | string  | Extension extended number |
| userIdentifier* | string  | Account identifier        |
| userID*         | integer | Account ID                |

**Legend:**

- `*` - exactly one of the fields should be provided

#### Get Public No Poll

- **Tool Name**: `get-public-no-poll`
- **Description**: Retrieve public no poll.
- **Input Schema**:

| Parameter       | Type    | Description               |
|-----------------|---------|---------------------------|
| extendedNumber* | string  | Extension extended number |
| userIdentifier* | string  | Account identifier        |
| userID*         | integer | Account ID                |

**Legend:**

- `*` - exactly one of the fields should be provided

#### Get Call Rules Out

- **Tool Name**: `get-call-rules-out`
- **Description**: Retrieve call rules out.
- **Input Schema**:

| Parameter | Type    | Description |
|-----------|---------|-------------|
| ID        | integer | The ID      |

#### Get Call Rules Out Group

- **Tool Name**: `get-call-rules-out-group`
- **Description**: Retrieve call rules out group.
- **Input Schema**:

| Parameter | Type    | Description                     |
|-----------|---------|---------------------------------|
| userID    | integer | Account ID                      |
| status    | boolean | Filter by status (Default: false) |
| filter    | string  | Filter string                   |

#### Get Channel Group Poll

- **Tool Name**: `get-channel-group-poll`
- **Description**: Retrieve channel group poll.
- **Input Schema**:

| Parameter | Type    | Description            |
|-----------|---------|------------------------|
| channelID | integer | The ID for the channel |

#### Get Channel Groups

- **Tool Name**: `get-channel-groups`
- **Description**: Retrieve channel groups.
- **Input Schema**:

| Parameter | Type    | Description            |
|-----------|---------|------------------------|
| channelID | integer | The ID for the channel |
| filter    | string  | Filter string          |

---

## Error Handling

The VoipNow Provisioning MCP server offers robust error handling and detailed diagnostics to simplify troubleshooting.

### Error Categories

#### Configuration Errors

- **Missing credentials**: App ID or App Secret not provided
- **Invalid configuration**: Malformed JSON or missing required fields
- **File access issues**: Token file path not accessible or writable

#### Authentication Errors

- **Token generation failed**: Invalid app credentials or the VoipNow server is unavailable
- **Token expired**: Access token needs renewal (handled automatically)
- **MCP authorization failed**: Invalid or missing MCP auth token

#### API Communication Errors

- **Connection timeout**: The VoipNow server is not responding
- **Network issues**: DNS resolution or routing problems
- **API rate limiting**: Too many requests in a short timeframe

#### Validation Errors

- **Invalid parameters**: Missing required fields or invalid data types
- **Entity not found**: The specified user, organization, or service provider doesn't exist
- **Permission denied**: Insufficient privileges for requested operation

### Common Solutions

| Error Type                  | Solution                                                  |
| --------------------------- | --------------------------------------------------------- |
| **Configuration errors**    | Verify `config.json` syntax and file permissions          |
| **Authentication failures** | Check app credentials and connectivity to VoipNow server  |
| **API timeouts**            | Verify network connectivity and VoipNow server status     |
| **Parameter validation**    | Review tool documentation for required parameters         |
| **Permission errors**       | Make sure the VoipNow account has sufficient privileges   |

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
uv run src/main.py --log_transport console --config /path/to/config.json

# For syslog output
uv run src/main.py --log_transport syslog --config /path/to/config.json
```

**Validate configuration:**

```bash
# Test configuration without starting server
python -c "
import json
with open('/path/to/config.json') as f:
    config = json.load(f)
    print('Configuration valid:', bool(config.get('appId') and config.get('appSecret')))
"
```

### Support Resources

- **VoipNow API Documentation**: Check the official VoipNow API guides
- **Server Logs**: Monitor application logs for detailed error information
- **Network Diagnostics**: Use tools like `curl` to test the connectivity to VoipNow API
- **Configuration Validation**: Verify JSON syntax and required parameters

### Error Handling Best Practices

1. Always wrap SOAP calls in try-except blocks
2. Return meaningful error messages to users
3. Log errors with appropriate severity levels
4. Handle timeout and connection errors gracefully

---

## Prompt Examples

This guide explains how to provision and manage VoipNow entities with AI tools. Each example demonstrates how to write prompts that the AI can interpret and execute correctly.

### How to Use This Guide

#### Writing Effective Prompts

Every prompt must include these components:

1. **Entity type and hierarchy:**
   - Specify the entity type (ServiceProvider/Organization/User/Extension).
   - Include parent-child relationships.
   - Example: "Create a user under organization ID 21"

2. **Required parameters:**
   - Always include mandatory fields (login, name, email).
   - Use descriptive, unique identifiers.
   - Format: standardized naming conventions

3. **Dependencies:**
   - Specify charging plans when needed.
   - Include necessary permissions and limits.
   - Define relationships between entities.

4. **Verification steps:**
   - Request confirmation of creation.
   - Validate permissions and settings.
   - Check entity relationships.

Here's a complete prompt example:
```
"Create a complete phone system setup:
1. Create organization 'TestOrg' under default service provider
2. Set unlimited permissions for the organization
3. Create a user 'support_admin' under this organization
4. Configure user permissions for all extension types
5. Create extensions:
   - Queue (ext: 100)
   - IVR (ext: 200)
   - Conference (ext: 300)
6. Verify all entities were created properly"
```

### Basic Entity Management Examples

#### 1. Complete Organization Setup

```prompt
"Set up a new organization with all necessary components:
1. Create organization 'SupportTeam':
   - Login: support_org
   - Company: Support Operations
   - Email: support@example.com
2. Configure unlimited permissions for:
   - User management
   - Extension creation
   - Storage
   - API access
3. Create default charging plan
4. Verify organization setup"
```

#### 2. Multi-User Department Creation

```prompt
"Create a complete support department:
1. Create parent user 'support_admin':
   - Full administrative rights
   - Unlimited extension creation
   - Charging plan access
2. Create team leads (3 users):
   - Queue management permissions
   - Conference hosting rights
3. Create support agents (5 users):
   - Basic phone permissions
   - Queue member access
4. Set up extensions for each user type"
```

#### 3. Extension Suite Creation

```prompt
"Create a complete extension suite for support operations:
1. Set up main user with all permissions
2. Create extensions in order:
   - Main Queue (100): Support Queue
   - IVR (200): Welcome Menu
   - Conference (300): Team Meetings
   - Voicemail (400): Message Center
   - Callback (500): Return Calls
   - Intercom (600): Announcements
3. Verify all extensions are properly linked
4. Configure basic settings for each"
```

### Complex Provisioning Scenarios

#### 1. Multi-Department Call Center Setup

```prompt
"Create a complete call center infrastructure:
1. Create main organization 'CallCenter':
   - Set unlimited permissions
   - Configure charging plan
2. Create department structure:
   a. Sales Department:
      - Manager user with full permissions
      - Team queue extension (101)
      - Conference room (301)
      - 5 agent users with phone extensions
   b. Support Department:
      - Manager user with full permissions
      - Priority queue extension (102)
      - Conference room (302)
      - IVR system (201)
      - 10 agent users with phone extensions
   c. Technical Department:
      - Manager user with full permissions
      - Emergency queue (103)
      - Conference room (303)
      - 3 specialist users with phone extensions
3. Create shared resources:
   - Main IVR (200)
   - General voicemail (400)
   - Callback system (500)
4. Verify complete setup"
```

#### 2. Branch Office Deployment

```prompt
"Set up a new branch office with hierarchical structure:
1. Create branch organization:
   - Region-specific settings
   - Custom charging plan
   - API access enabled
2. Department Structure:
   - Create 3 department managers
   - Set up team hierarchies
   - Configure extension ranges:
     * Dept 1: 100-199
     * Dept 2: 200-299
     * Dept 3: 300-399
3. Extension Setup:
   - Queue for each department
   - Shared conference rooms
   - Department-specific IVRs
4. Permission Management:
   - Department-level access control
   - Resource sharing rules
   - Monitoring capabilities"
```

#### 3. Automated System Migration

```prompt
"Migrate and upgrade existing setup:
1. Create new organization structure
2. For each department:
   - Create corresponding users
   - Set up matching extensions
   - Configure permissions
   - Verify charging plans
3. Create shared resources:
   - Queue systems
   - Conference rooms
   - IVR menus
4. Validate complete setup:
   - Test all extensions
   - Verify permissions
   - Check charging plans"
```

### User Management

#### Create User
```prompt
Create a user under organization ID 21 with:
- Login: userZ789
- First Name: User
- Last Name: Auto
- Company: orgY456
- Email: userZ789@example.com
Use the MCP add tool with type User.
```

#### Set User Permissions
```prompt
Set all permissions and limits for user ID 22 to unlimited, including:
- Storage
- Extensions
- Concurrent calls
Enable sharing features:
- Share voicemail: everybody
- Share recordings: everybody
- Share call history: everybody
Use the MCP set_permissions_limits tool with type User.
```

### Extension Management Examples

#### 1. Queue System Setup

```prompt
"Create a complete queue system:
1. Create queue manager user with permissions:
   - Queue management
   - Extension creation
   - Call monitoring
2. Set up queue structure:
   - Main queue (100): General Support
   - Priority queue (101): Premium Support
   - Overflow queue (102): High Volume
3. Configure for each queue:
   - Welcome messages
   - Agent assignments
   - Queue priorities"
```

#### 2. IVR Menu Creation

```prompt
"Set up multi-level IVR system:
1. Create IVR admin user with permissions
2. Create IVR structure:
   - Main menu (200): Welcome
   - Sales menu (201): Products
   - Support menu (202): Help
3. Link IVRs to appropriate:
   - Queue extensions
   - Voicemail boxes
   - Callback systems"
```

#### 3. Conference System

```prompt
"Create conference center setup:
1. Create conference admin user
2. Set up conference rooms:
   - Main conference (300): All Hands
   - Team rooms (301-305): Department Meetings
   - Training room (306): Learning Sessions
3. Configure each with:
   - Access controls
   - Recording settings
   - Participant limits"
```

#### 4. Extension Integration

```prompt
"Create integrated extension system:
1. Set up user hierarchy:
   - Admin users for each type
   - Team leaders with mixed permissions
   - Regular users with basic access
2. Create linked extensions:
   - Queue -> IVR routing
   - Conference -> Queue integration
   - Voicemail -> Callback system
3. Configure routing rules
4. Test all integrations"
```

### Charging Plan Management

#### Get Charging Plans
```prompt
Retrieve available charging plans for:
- All plans: Use MCP get_charging_plan tool with type Billing
- Specific user's plans: Add userID parameter
- Default plans only: Add default parameter true
```

#### Query Specific Plan
```prompt
Get details of charging plan ID 1:
- Use MCP get_charging_plan tool
- Add specific plan ID
- Check plan type (postpaid/prepaid)
- Verify if it's a default plan
```

### Complete Provisioning Example

```prompt
Provision a phone terminal extension in VoipNow using only the available MCP tools from the VoipNow Provisioning MCP server. The workflow must be fully automated and include:

1. Create a service provider (reseller) with a random name and email using only the MCP add tool.
2. Set all permissions, limits, and expiration for the service provider to "unlimited" using only the MCP set_permissions_limits tool.
3. Create a postpaid charging plan under the service provider using only the MCP tools.
4. Create an organization under the service provider with a random name and email using only the MCP add tool.
5. Set all permissions, limits, and expiration for the organization to "unlimited" using only the MCP set_permissions_limits tool.
6. Create a postpaid charging plan under the organization using only the MCP tools.
7. Create a user under the organization with a random name and email using only the MCP add tool.
8. Set all permissions, limits, and expiration for the user to "unlimited" using only the MCP set_permissions_limits tool.
9. Create a phone terminal extension for the user, using a random valid extension number and label, and auto-generate the password, using only the MCP add_extension tool.

All steps must use only the MCP tools, and all dependencies (IDs, parent-child relationships) must be respected. The process should be robust, fully automated, and require no manual input at any step.
```

### Troubleshooting and Best Practices

#### Common Setup Patterns

1. **Entity creation order:**
   - Create parent entities before children.
   - Set permissions before creating extensions.
   - Verify each step before proceeding.

2. **Permission management:**
   - Start with minimal permissions.
   - Use unlimited only when needed.
   - Verify access after changes.

3. **Extension numbering:**
   - Use consistent ranges per department.
   - Leave place for future expansion.
   - Document number assignments.

#### Error Prevention

1. **Before creating entities:**
   - Verify that the parent exists.
   - Check charging plan availability.
   - Confirm permission requirements.

2. **During setup:**
   - Validate each step of the creation process.
   - Check parent-child relationships.
   - Verify permission propagation.

3. **After changes:**
   - Test affected extensions.
   - Verify user access.
   - Document configuration.

#### Best Practices

1. **Organization structure:**
   - Use clear naming conventions.
   - Maintain logical hierarchies.
   - Document relationships.

2. **Permission management:**
   - Follow least-privilege principle.
   - Use role-based access.
   - Regular permission audits

3. **Extension management:**
   - Consistent numbering scheme
   - Clear labeling standards
   - Regular configuration reviews

4. **System maintenance:**
   - Regular permission checks
   - Configuration validation
   - Documentation updates

#### Recovery Procedures

1. **Extension issues:**
   ```prompt
   "Verify and repair extension 0003*101:
   1. Check extension exists
   2. Verify user permissions
   3. Validate charging plan
   4. Reset if necessary
   5. Test functionality"
   ```

2. **Permission problems:**
   ```prompt
   "Fix user permissions for support team:
   1. Check current permissions
   2. Compare with required setup
   3. Update as needed
   4. Verify changes
   5. Test access"
   ```

3. **System verification:**
   ```prompt
   "Validate complete setup:
   1. List all extensions
   2. Check user permissions
   3. Verify relationships
   4. Test integrations
   5. Document status"
   ```

#### Common Parameters

- **type**: Entity type (ServiceProvider, Organization, User, Extension)
- **ID**: Entity identifier
- **identifier**: Alternative unique identifier
- **parentID**: ID of parent entity
- **login**: Unique login name
- **email**: Contact email
- **company**: Company name
- **extensionNo**: Extension number for phone terminal extensions
- **label**: Descriptive label
- **passwordAuto**: Boolean for auto-generating passwords

#### Error Handling

Always check response codes and messages. Common errors:
- 405: Method not allowed
- 404: Entity not found
- 409: Conflict (duplicate entry)
- 400: Invalid parameters
- 403: Permission denied

Handle errors appropriately and ensure proper cleanup if a step fails.

---

## For Developers

### Tool Templating Guide

#### Quick Start

Create new tools in `/src/tools/` using Python files with registry-based configurations.

### Basic Tool Template

```python
import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "YourType"

# Tool registry containing all tool configurations
TOOL_REGISTRY = {
    "your_tool": {
        "allowed_keys": ["param1", "param2", "optionalParam"],
        "method_type": "YourMethodType",
        "tool_name": "your-tool",
        "tool_description": "Description of what your tool does",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of required parameter"
                },
                "param2": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Description of integer parameter"
                },
                "optionalParam": {
                    "type": "string",
                    "description": "Description of optional parameter"
                },
                "enumParam": {
                    "type": "string",
                    "enum": ["value1", "value2", "value3"],
                    "description": "Parameter with allowed values"
                }
            },
            "required": ["param1", "param2"]
        }
    }
}

# Generate tool schemas
def _create_tool_schema(tool_config: Dict[str, Any]) -> types.Tool:
    """Create a Tool schema from configuration."""
    return types.Tool(
        name=tool_config["tool_name"],
        description=tool_config["tool_description"],
        inputSchema=tool_config["input_schema"]
    )

# Create tool schemas
TOOL_SCHEMAS = {
    func_name: _create_tool_schema(config)
    for func_name, config in TOOL_REGISTRY.items()
}

# Backwards compatibility constants
YOUR_TOOL_NAME = TOOL_REGISTRY["your_tool"]["tool_name"]
YOUR_TOOL_SCHEMA = TOOL_SCHEMAS["your_tool"]

async def your_tool(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Description of what your tool does.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
        logger (logging.Logger): Logger instance for debugging.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    tool_config = TOOL_REGISTRY["your_tool"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        TOOL_SCHEMAS["your_tool"],
        TYPE
    )
```

### Advanced Tool Template

For tools with complex validation and conditional logic:

```python
import utils.utils as utils
import mcp.types as types
import logging
from typing import Dict, Any

# Define type
TYPE = "AdvancedType"

# Tool registry with conditional validation
TOOL_REGISTRY = {
    "advanced_tool": {
        "allowed_keys": ["type", "param1", "param2", "conditionalParam"],
        "method_type": "AdvancedMethodType",
        "tool_name": "advanced-tool",
        "tool_description": "Advanced tool with conditional validation",
        "input_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Type of operation",
                    "enum": ["TypeA", "TypeB", "TypeC"]
                },
                "param1": {
                    "type": "string",
                    "description": "Required parameter"
                },
                "param2": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Integer parameter"
                },
                "conditionalParam": {
                    "type": "string",
                    "description": "Parameter required only for TypeA"
                },
                "arrayParam": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Array of string values"
                },
                "dateParam": {
                    "type": "string",
                    "format": "date",
                    "description": "Date parameter in YYYY-MM-DD format"
                }
            },
            "required": ["type", "param1"],
            "allOf": [
                {
                    "if": {"properties": {"type": {"const": "TypeA"}}},
                    "then": {"required": ["conditionalParam"]}
                }
            ]
        }
    }
}

# Generate tool schemas
def _create_tool_schema(tool_config: Dict[str, Any]) -> types.Tool:
    """Create a Tool schema from configuration."""
    return types.Tool(
        name=tool_config["tool_name"],
        description=tool_config["tool_description"],
        inputSchema=tool_config["input_schema"]
    )

# Create tool schemas
TOOL_SCHEMAS = {
    func_name: _create_tool_schema(config)
    for func_name, config in TOOL_REGISTRY.items()
}

# Backwards compatibility constants
ADVANCED_TOOL_NAME = TOOL_REGISTRY["advanced_tool"]["tool_name"]
ADVANCED_TOOL_SCHEMA = TOOL_SCHEMAS["advanced_tool"]

async def advanced_tool(
    arguments: dict, config: dict, logger: logging.Logger
) -> list[types.TextContent]:
    """
    Advanced tool with conditional logic.

    Args:
        arguments (dict): The input arguments.
        config (dict): The configuration dictionary containing the VoipNow URL and token.
        logger (logging.Logger): Logger instance for debugging.

    Returns:
        list[types.TextContent]: The response as a list of TextContent objects.
    """
    # Custom preprocessing logic
    if arguments.get("type") == "TypeA" and "conditionalParam" not in arguments:
        raise ValueError("conditionalParam is required for TypeA")

    tool_config = TOOL_REGISTRY["advanced_tool"]
    return await utils._execute_operation(
        arguments, config, logger,
        tool_config["method_type"],
        tool_config["allowed_keys"],
        TOOL_SCHEMAS["advanced_tool"],
        TYPE
    )
```

#### Naming Convention

- File: `tool_name.py`
- Registry key: `"tool_function"`
- Tool name: `"tool-name"` (kebab-case)
- Function: `tool_function` (snake_case)
- Constants: `TOOL_NAME`, `TOOL_SCHEMA`

#### Common Patterns

**JSON Schema types:**
```python
# Basic types
{"type": "string", "description": "String parameter"}
{"type": "integer", "minimum": 1, "description": "Positive integer"}
{"type": "boolean", "default": False, "description": "Boolean parameter"}

# Enums
{"type": "string", "enum": ["value1", "value2"], "description": "Allowed values"}

# Arrays
{"type": "array", "items": {"type": "string"}, "description": "Array of strings"}

# Conditional validation
"allOf": [
    {
        "if": {"properties": {"type": {"const": "User"}}},
        "then": {"required": ["userSpecificParam"]}
    }
]

# Alternative requirements
"oneOf": [
    {"required": ["param1"]},
    {"required": ["param2"]},
    {"required": ["param3"]}
]
```

**Registry structure:**
```python
TOOL_REGISTRY = {
    "function_name": {
        "allowed_keys": ["param1", "param2"],  # Parameters passed to API
        "method_type": "APIMethodName",        # SOAP method name
        "tool_name": "kebab-case-name",        # MCP tool name
        "tool_description": "Description",     # Tool description
        "input_schema": {...}                  # JSON Schema
    }
}
```

**Always use:**
- `utils._execute_operation()` for API calls
- `additionalProperties": False` in schemas
- Proper docstrings with Args and Returns
- `types.TextContent` return type
- Backwards compatibility constants

#### Directory Structure

**Single tool files:**
```
src/tools/
├── your_tool.py
└── another_tool.py
```

**Category-based organization:**
```
src/tools/
├── entity/
│   ├── __init__.py
│   ├── add.py
│   ├── get.py
│   └── delete.py
├── billing.py
└── channel.py
...
```

#### Documentation

Add new tools to `/doc/3-tools.md` following the existing format.

---

**End of Documentation**
