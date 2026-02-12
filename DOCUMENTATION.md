# VoipNow MCP Servers - Complete Documentation

This repository contains **two separate MCP (Model Context Protocol) servers** for VoipNow, each with a distinct scope and purpose. These servers enable AI assistants to interact with VoipNow platforms for different operational needs.

## Table of Contents

1. [Overview](#overview)
2. [Available MCP Servers](#available-mcp-servers)
3. [Quick Start](#quick-start)
4. [Requirements](#requirements)
5. [General Configuration](#general-configuration)
6. [Transport Types](#transport-types)
7. [Security Configuration](#security-configuration)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This repository provides **two independent MCP servers** that work with VoipNow platforms:

1. **VoipNow Calls** - Real-time call management and communication
2. **VoipNow Provisioning** - Entity provisioning and administrative operations

Each server runs independently, has its own documentation, and can be deployed separately based on your needs.

---

## Available MCP Servers

### 🔵 VoipNow Calls MCP Server

**Purpose:** Real-time call management and communication features

**Technology:** Node.js / TypeScript

**Use Cases:**
- Managing active phone calls
- Call control operations (hold, transfer, park, monitor)
- CDR (Call Detail Records) management
- Extension presence and queue management
- Fax operations
- Real-time call events

**Tools Available:** 20+ call management tools

**📖 Complete Documentation:** [calls/DOCUMENTATION.md](calls/DOCUMENTATION.md)

**Key Features:**
- Phone call creation and management
- Advanced call control (hold/unhold, park/unpark, transfer)
- Call monitoring and recording
- Queue agent management
- Phone call events scheduling
- Fax sending capabilities

### 🟢 VoipNow Provisioning MCP Server

**Purpose:** Entity provisioning and administrative operations

**Technology:** Python / uv

**Use Cases:**
- User and organization management
- Service provider administration
- Extension provisioning
- Permissions and limits configuration
- Billing and charging plan management
- PBX configuration
- System reports

**Tools Available:** 67+ provisioning tools across 6 categories

**📖 Complete Documentation:** [provisioning/DOCUMENTATION.md](provisioning/DOCUMENTATION.md)

**Key Features:**
- Entity management (users, organizations, service providers)
- Permission and limit management
- Extension provisioning and configuration
- Billing and charging plan operations
- PBX settings and device management
- Comprehensive reporting

---

## Quick Start

### Step 1: Choose Your MCP Server

Depending on your needs, you can deploy one or both servers:

| Need | Server | Documentation |
|------|--------|---------------|
| **Real-time call management** | VoipNow Calls | [calls/DOCUMENTATION.md](calls/DOCUMENTATION.md) |
| **User/entity provisioning** | VoipNow Provisioning | [provisioning/DOCUMENTATION.md](provisioning/DOCUMENTATION.md) |
| **Both capabilities** | Deploy both servers | See both documentation files |

### Step 2: Follow Server-Specific Setup

Each server has its own complete setup guide:

**For VoipNow Calls:**
- 📖 [Complete Setup Guide](calls/DOCUMENTATION.md#setup)
- 🐳 [Container Installation](calls/DOCUMENTATION.md#container-support-optional)
- ⚙️ [Configuration](calls/DOCUMENTATION.md#configuration)

**For VoipNow Provisioning:**
- 📖 [Complete Setup Guide](provisioning/DOCUMENTATION.md#setup)
- 🐳 [Container Installation](provisioning/DOCUMENTATION.md#container-support-optional)
- ⚙️ [Configuration](provisioning/DOCUMENTATION.md#configuration)

### Step 3: Deploy Using Containers (Recommended)

Both servers support Docker/Podman deployment. See individual server documentation for:
- Building container images
- Configuration setup
- Running containers
- Health checks

---

## Requirements

### General Requirements

Both servers require:

| Component          | Minimum Version | Purpose                                   |
| ------------------ | --------------- | ----------------------------------------- |
| **Docker/Podman**  | Latest          | Container runtime (recommended deployment) |
| **VoipNow**        | `5.6+`          | VoipNow platform API integration          |

### Server-Specific Requirements

**VoipNow Calls:**
- Node.js 18+ (if not using containers)
- See [calls/DOCUMENTATION.md#requirements](calls/DOCUMENTATION.md#requirements)

**VoipNow Provisioning:**
- Python 3.10+ with uv (if not using containers)
- See [provisioning/DOCUMENTATION.md#requirements](provisioning/DOCUMENTATION.md#requirements)

> [!TIP]
> **Using containers?** You don't need to install Node.js or Python locally. The container images include all runtime dependencies.

---

## General Configuration

Both MCP servers use similar configuration patterns but have different tool sets and capabilities.

### VoipNow App Credentials

Both servers authenticate to VoipNow using App credentials:

1. **Register an App in VoipNow:**
   - Navigate to: `Unified Communications` → `Integrations` → `Apps`
   - Create a new app with "trusted app" enabled
   - Note the App ID and App Secret

2. **Create Configuration File:**

Both servers use a `config.json` file with similar structure:

```json
{
  "appId": "your-app-id",
  "appSecret": "your-app-secret",
  "voipnowHost": "https://your-voipnow-host.com",
  "voipnowTokenFile": "/path/to/.access_token",
  "authTokenMCP": "your-mcp-auth-token",
  "logLevel": "info"
}
```

For detailed configuration instructions, see:
- [VoipNow Calls Configuration](calls/DOCUMENTATION.md#configuration)
- [VoipNow Provisioning Configuration](provisioning/DOCUMENTATION.md#configuration)

---

## Transport Types

Both MCP servers support multiple transport types for communication:

### STDIO Transport

> [!NOTE]
> **Best for: Local development and simple integrations**

- **Pros**: Simplest setup, no network configuration needed
- **Cons**: Client and server must run on the same machine
- **Use case**: Development, CLI tools, local integrations

### HTTP Transports

> [!NOTE]
> **Best for: Production deployments and remote access**

| Transport           | Status          | Use Case                                       |
| ------------------- | --------------- | ---------------------------------------------- |
| **Streamable HTTP** | **Recommended** | Production, multiple clients, web integrations |
| **SSE**             | **Deprecated**  | Legacy support only                            |

**Default Ports:**
- VoipNow Calls: `3000`
- VoipNow Provisioning: `8000`

For detailed transport configuration, see the server-specific documentation:
- [VoipNow Calls Transport Setup](calls/DOCUMENTATION.md#mcp-transport-setup)
- [VoipNow Provisioning Transport Setup](provisioning/DOCUMENTATION.md#mcp-transport-setup)

---

## Security Configuration

> [!CAUTION]
> **Security is critical** when using HTTP transports, since MCP servers operate with user-level privileges.

### When Authentication is Required

- **Required**: HTTP transports started with `--secure`
- **Not required**: STDIO transport (local only)

### Generate Secure Token

```bash
# Generate a random token (recommended: 32+ characters)
tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32 && echo
```

Add the token to your `config.json`:

```json
{
  "authTokenMCP": "your-generated-token-here"
}
```

### Firewall Configuration

If running HTTP transports, ensure the ports are accessible:

```bash
# For VoipNow Calls (port 3000)
sudo firewall-cmd --permanent --add-port=3000/tcp

# For VoipNow Provisioning (port 8000)
sudo firewall-cmd --permanent --add-port=8000/tcp

sudo firewall-cmd --reload
```

For complete security setup, see:
- [VoipNow Calls Security](calls/DOCUMENTATION.md#security)
- [VoipNow Provisioning Security](provisioning/DOCUMENTATION.md#security)

---

## Testing

### Testing with AI Clients

#### Claude Desktop

Claude Desktop provides a comprehensive testing environment for MCP servers.

**Setup steps:**

1. Install Claude Desktop from `https://claude.ai/download`
2. Enable Developer Mode (`Help` → `Enable Developer Mode`)
3. Configure the MCP server in `Settings` → `Developer` → `Edit Config`

**Example Configuration (HTTP):**

```json
{
  "mcpServers": {
    "voipnow-calls": {
      "url": "http://SERVER_IP:3000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_AUTH_TOKEN"
      }
    },
    "voipnow-provisioning": {
      "url": "http://SERVER_IP:8000/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_AUTH_TOKEN"
      }
    }
  }
}
```

### Testing with MCP Inspector

The MCP Inspector provides a web-based interface for testing and debugging MCP servers.

```bash
npx @modelcontextprotocol/inspector
```

The inspector opens at `http://127.0.0.1:6274`.

**Connection Steps:**
- **HTTP**: Start the server, add URL, include `Authorization` if secure, click Connect
- **STDIO**: Set command and args, add env vars if needed, click Connect

### Verification Checklist

- [ ] Server starts without errors
- [ ] Client can connect to server
- [ ] Authentication works (if enabled)
- [ ] All expected tools are listed
- [ ] Tools execute and return expected results
- [ ] Errors are handled gracefully
- [ ] Responses are within acceptable time limits

For detailed testing instructions, see:
- [VoipNow Calls Testing](calls/DOCUMENTATION.md#testing)
- [VoipNow Provisioning Testing](provisioning/DOCUMENTATION.md#testing)

---

## Troubleshooting

### Connection Issues

**Server not responding:**
- Verify server is running: `ps aux | grep node` (Calls) or `ps aux | grep uv` (Provisioning)
- Check port availability: `ss -tlnp | grep :PORT`
- Verify firewall settings
- Check server logs for errors

**Authentication failures:**
- Verify token format and validity
- Check authorization headers
- Ensure tokens match between server and client

### Tool Issues

**Tools not appearing:**
- Restart Claude Desktop after configuration changes
- Verify JSON syntax in configuration file
- Check server logs for tool registration errors

**Tool execution failures:**
- Verify required parameters are provided
- Check API credentials and permissions
- Review error messages in client and server logs

### Server-Specific Troubleshooting

For detailed troubleshooting guides:
- [VoipNow Calls Error Handling](calls/DOCUMENTATION.md#error-handling)
- [VoipNow Provisioning Error Handling](provisioning/DOCUMENTATION.md#error-handling)

---

## Deployment Architecture

### Single Server Deployment

Deploy only the server you need:

```
┌─────────────────┐
│   AI Client     │
│ (Claude, etc.)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VoipNow Calls  │  ◄── For call management only
│   MCP Server    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VoipNow API    │
└─────────────────┘
```

### Dual Server Deployment

Deploy both servers for complete functionality:

```
┌─────────────────┐
│   AI Client     │
│ (Claude, etc.)  │
└────┬──────┬─────┘
     │      │
     │      └──────────────────┐
     ▼                         ▼
┌─────────────────┐   ┌─────────────────────┐
│  VoipNow Calls  │   │ VoipNow Provisioning │
│   MCP Server    │   │     MCP Server       │
└────────┬────────┘   └──────────┬──────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
            ┌─────────────────┐
            │  VoipNow API    │
            └─────────────────┘
```

---

## Additional Resources

### Server Documentation

- **[VoipNow Calls Complete Guide](calls/DOCUMENTATION.md)** - Setup, tools, configuration, examples
- **[VoipNow Provisioning Complete Guide](provisioning/DOCUMENTATION.md)** - Setup, tools, configuration, examples

### Quick Reference

- **[VoipNow Calls README](calls/README.md)** - Quick overview and capabilities
- **[VoipNow Provisioning README](provisioning/README.md)** - Quick overview and capabilities

### Project Information

- **[Main README](README.md)** - Repository overview and quick start
- **[License](LICENSE)** - MIT License
- **[Security Fixes](SECURITY_FIXES.md)** - Recent security improvements

---

## Support

For issues, questions, or contributions:
- **GitHub Issues:** [https://github.com/4psainc/mcp-voipnow/issues](https://github.com/4psainc/mcp-voipnow/issues)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
