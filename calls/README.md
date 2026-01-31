# MCP VoipNow Calls

The VoipNow Calls MCP server delivers extensive call management and communication features for VoipNow platforms. It allows AI assistants to use the VoipNow UnifiedAPI to handle phone calls, call history, extensions, and fax operations.

This guide walks you through setting up and using the VoipNow Calls MCP server to manage calls, extensions, CDR records, and fax operations.

## Table of contents

- [Key Capabilities](#key-capabilities)
- [Documentation](#documentation)
- [Quick Links](#quick-links)

## Key capabilities

### Call management

- Phone calls: create, delete, list, and manage active phone calls
- Call control: monitor, hold/unhold, park/unpark, transfer, and record calls
- Advanced operations: pickup, barge-in, whisper, and transfer to voicemail

### Extension management

- Presence monitoring for extensions
- Queue agents list/update
- Phone call events create/list/update/delete

### Communication services

- CDR records (history and statistics)
- Fax services
- Real-time call control

### Available tools summary

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

## Documentation

**📖 [Complete Documentation](DOCUMENTATION.md)** - Single-page comprehensive guide covering:

- **Setup & Installation** - Requirements, quick start, command-line arguments
- **Configuration** - VoipNow App credentials, container support, transport options
- **Tools Reference** - Complete documentation for all 20+ call management tools
- **Error Handling** - Troubleshooting, debugging tips, and common solutions
- **Prompt Examples** - Real-world usage scenarios and best practices
- **For Developers** - Tool templating guide and development guidelines

## Quick Links

- [Setup Guide](DOCUMENTATION.md#setup) - Get started with installation and configuration
- [Tool Reference](DOCUMENTATION.md#tools-reference) - Complete tool documentation
- [Usage Examples](DOCUMENTATION.md#prompt-examples) - Learn how to use the tools effectively
- [Troubleshooting](DOCUMENTATION.md#error-handling) - Common issues and solutions
