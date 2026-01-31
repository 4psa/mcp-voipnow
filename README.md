# VoipNow MCP Servers

This repository contains **two separate MCP (Model Context Protocol) servers** for VoipNow, each with a distinct scope and purpose. These servers enable AI assistants to interact with VoipNow platforms for different operational needs.

## Overview

This repository provides **two independent MCP servers** that work with VoipNow platforms:

1. **VoipNow Calls** - Real-time call management and communication
2. **VoipNow Provisioning** - Entity provisioning and administrative operations

Each server runs independently, has its own documentation, and can be deployed separately based on your needs.

## Available MCP Servers

### 🔵 VoipNow Calls

**Purpose:** Real-time call management and communication features

**Technology:** Node.js / TypeScript

**Key Features:**
- Managing active phone calls
- Call control operations (hold, transfer, park, monitor)
- CDR (Call Detail Records) management
- Extension presence and queue management
- Fax operations
- Real-time call events

**📖 [Complete Documentation](calls/DOCUMENTATION.md)** | **[Quick Overview](calls/README.md)**

---

### 🟢 VoipNow Provisioning

**Purpose:** Entity provisioning and administrative operations

**Technology:** Python / uv

**Key Features:**
- User and organization management
- Service provider administration
- Extension provisioning
- Permissions and limits configuration
- Billing and charging plan management
- PBX configuration
- System reports

**📖 [Complete Documentation](provisioning/DOCUMENTATION.md)** | **[Quick Overview](provisioning/README.md)**

## Quick Start

Choose the server(s) you need and follow the server-specific setup guide:

| Need | Server | Setup Guide |
|------|--------|-------------|
| **Real-time call management** | VoipNow Calls | [calls/DOCUMENTATION.md](calls/DOCUMENTATION.md) |
| **User/entity provisioning** | VoipNow Provisioning | [provisioning/DOCUMENTATION.md](provisioning/DOCUMENTATION.md) |
| **Both capabilities** | Deploy both servers | See both documentation files |

> [!TIP]
> Both servers support Docker/Podman deployment. See individual server documentation for complete setup instructions.

## Documentation

**📖 [Complete Documentation](DOCUMENTATION.md)** - Single-page comprehensive guide covering:
- Quick Start
- Requirements
- Available Servers & Tools
- Installation (Docker/Podman)
- Transport Configuration
- Security Setup
- Testing & Verification
- Troubleshooting

### Server-Specific Documentation
- [VoipNow Calls](calls/README.md) - Call management and communication features
- [VoipNow Provisioning](provisioning/README.md) - Entity provisioning and management

## License

This project is licensed under the MIT License.
