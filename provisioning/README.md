# MCP VoipNow Provisioning

The VoipNow Provisioning MCP server provides robust service provisioning and entity management for VoipNow platforms. It allows AI assistants to interact with the VoipNow API to manage users, organizations, service providers, and their related configurations.

This guide explains how to set up and use the VoipNow Provisioning MCP server to manage entities, users, organizations, and service providers.

## Table of contents

- [Key Capabilities](#key-capabilities)
- [Documentation](#documentation)
- [Quick Links](#quick-links)

## Key capabilities

### Entity management

- Users: Create, edit, delete, and manage user accounts
- Organizations: Manage organizational structures and hierarchies
- Service Providers: Handle service provider configurations and settings

### Permission & limit management

- Access control: Set control panel access and user roles
- Resource limits: Configure extension limits, storage quotas, and concurrent call limits
- Permission sets: Manage feature permissions and administrative rights

### Extension management

- Extension types: Support for phone terminal, queue, IVR, voicemail, conference, and other extension types
- Configuration: Set up extension parameters, passwords, and labels
- Bulk operations: Retrieve and manage multiple extensions

### Advanced operations

- Organizational movement: Transfer organizations between service providers
- Charging plans: Manage billing configuration and charging plans
- Group management: Handle user groups and permission sharing
- Status management: Control account and phone service status

### Available tools summary

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

## Documentation

**📖 [Complete Documentation](DOCUMENTATION.md)** - Single-page comprehensive guide covering:

- **Setup & Installation** - Requirements, quick start, command-line arguments
- **Configuration** - VoipNow App credentials, container support, transport options
- **Tools Reference** - Complete documentation for all 67 provisioning tools across 6 categories
- **Error Handling** - Troubleshooting, debugging tips, and common solutions
- **Prompt Examples** - Real-world provisioning scenarios and best practices
- **For Developers** - Tool templating guide and development guidelines

## Quick Links

- [Setup Guide](DOCUMENTATION.md#setup) - Get started with installation and configuration
- [Tool Reference](DOCUMENTATION.md#tools-reference) - Complete tool documentation by category
- [Usage Examples](DOCUMENTATION.md#prompt-examples) - Learn how to use the tools effectively
- [Troubleshooting](DOCUMENTATION.md#error-handling) - Common issues and solutions
