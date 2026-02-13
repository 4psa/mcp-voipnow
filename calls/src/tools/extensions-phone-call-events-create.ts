import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const extensionsPhoneCallEventsCreateToolName = "extensions-phone-call-events-create";
export const extensionsPhoneCallEventsCreateToolDescription = "Allows adding new phone call events in particular contexts such as User, Organization or global.";

// Tool Schema
export const ExtensionsPhoneCallEventsCreateToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the Extension for which the event is added. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension for which the event is added. Allowed Extension types: Phone Terminal, Queue, Conference, and IVR. Cannot be set to @self."),
    //payload params
    type: z.enum(["0", "1", "2", "3", "4"]).optional().describe("Type of the Phone Call Event. Possible values: 0 - Dial-In, 1 - Dial-Out, 2 - Hangup, 3 - Answer incoming call, 4 - Answer outgoing call."),
    method: z.enum(["0", "1"]).optional().describe("The HTTP method used by the server to access the URL when an event occurs. Possible values: 0 - GET, 1 - POST"),
    note: z.string().optional().describe("Notes about the event."),
    url: z.string().optional().describe("The URL that is accessed when the extension receives, makes or terminates a phone call. Must be encoded using the RFC 3986."),
    status: z.enum(["0", "1"]).optional().describe("The status of the event. Possible values: 0 - disabled, 1 - enabled"),
}).strict();

// Tool definition
export const EXTENSIONS_PHONE_CALL_EVENTS_CREATE_TOOL: Tool = {
    name: extensionsPhoneCallEventsCreateToolName,
    description: extensionsPhoneCallEventsCreateToolDescription,
    inputSchema: toJsonSchemaCompat(ExtensionsPhoneCallEventsCreateToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runExtensionsPhoneCallEventsCreateTool(
    args: z.infer<typeof ExtensionsPhoneCallEventsCreateToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, type, method, note, url, status } = ExtensionsPhoneCallEventsCreateToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsPhoneCallEventsCreateToolName} tool...`);
        var paramsExtensionsPhoneCallEventsCreateURL = '';
        let payload = {};

        // Check extension format
        if (!utils.validateExtension(extension) || extension === '@self') {
            if (extension === '@self') {
                throw new Error(utils.errorMessageExtensionSelf);
            }
            throw new Error(utils.errorMessageExtension);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsExtensionsPhoneCallEventsCreateURL = paramsExtensionsPhoneCallEventsCreateURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/phoneCallEvents/` : ''
        );

        payload = {
            type: type,
            method: method,
            note: note,
            url: url,
            status: status
        };

        logger.debug(`Creating phone call event for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsPhoneCallEventsCreateURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(config.voipnowUrl, `/uapi/extensions/${paramsExtensionsPhoneCallEventsCreateURL}`), {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${config.voipnowToken}`,
                "User-Agent": userAgent.toString(),
            },
            body: JSON.stringify(payload),
            redirect: 'manual', // Prevent automatic redirection
            ...(config.agent && { agent: config.agent }),
        });

        // Handle non-2xx responses
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
            content: [
                {
                    type: "text",
                    text: JSON.stringify(responseData),
                },
            ],
        };
    } catch (error) {
        const errorMessage = `Error creating phone call event: ${error instanceof Error ? error.message : String(error)}`
        logger.error(errorMessage);
        return {
            content: [
                {
                    type: "text",
                    text: errorMessage,
                },
            ],
        };
    }
}