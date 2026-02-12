import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const extensionsPhoneCallEventsUpdateToolName = "extensions-phone-call-events-update";
export const extensionsPhoneCallEventsUpdateToolDescription = "Allows allows updating existing phone call events in particular contexts such as User, Organization or global.";

// Tool Schema
export const ExtensionsPhoneCallEventsUpdateToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the Extension for which the event is updated. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension for which the event is updated. Allowed Extension types: Phone Terminal, Queue, Conference, and IVR. Cannot be set to @self."),
    eventType: z.enum(["0", "1", "2", "3", "4"]).describe("Type of the Phone Call Event. Possible values: 0 - Dial-In, 1 - Dial-Out, 2 - Hangup, 3 - Answer incoming call, 4 - Answer outgoing call."),
    eventID: z.string().describe("The Id of the phone call event to be updated."),
    //payload params
    method: z.enum(["0", "1"]).optional().describe("The HTTP method used by the server to access the URL when an event occurs. Possible values: 0 - GET, 1 - POST"),
    note: z.string().optional().describe("Notes about the event."),
    url: z.string().optional().describe("The URL that is accessed when the extension receives, makes or terminates a phone call. Must be encoded using the RFC 3986."),
    status: z.enum(["0", "1"]).optional().describe("The status of the event. Possible values: 0 - disabled, 1 - enabled"),
}).strict();


// Tool definition
export const EXTENSIONS_PHONE_CALL_EVENTS_UPDATE_TOOL: Tool = {
    name: extensionsPhoneCallEventsUpdateToolName,
    description: extensionsPhoneCallEventsUpdateToolDescription,
    inputSchema: toJsonSchemaCompat(ExtensionsPhoneCallEventsUpdateToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runExtensionsPhoneCallEventsUpdateTool(
    args: z.infer<typeof ExtensionsPhoneCallEventsUpdateToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, eventType, eventID, method, note, url, status } = ExtensionsPhoneCallEventsUpdateToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsPhoneCallEventsUpdateToolName} tool...`);
        var paramsExtensionsPhoneCallEventsDeleteURL = '';
        let payload = {}

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
        paramsExtensionsPhoneCallEventsDeleteURL = paramsExtensionsPhoneCallEventsDeleteURL.concat(
            modifiedUserId && extension && eventType && eventID ? `${modifiedUserId}/${extension}/phoneCallEvents/${eventType}/${eventID}/` : ''
        );

        payload = {
            method: method,
            note: note,
            url: url,
            status: status
        };

        logger.debug(`Updating phone call events for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsPhoneCallEventsDeleteURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/extensions/${paramsExtensionsPhoneCallEventsDeleteURL}`), {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "User-Agent": userAgent.toString(),
                "Authorization": `Bearer ${config.voipnowToken}`,
            },
            body: JSON.stringify(payload),
            redirect: 'manual' // Prevent automatic redirection
        });

        // Handle non-2xx responses
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 400 || response.status === 401 || response.status === 403 || response.status === 500) {
                const errorMessage = `{'code': ${errorData.error.code}, 'message': ${errorData.error.message}}`
                throw new Error(errorMessage);
            }
            const errorMessage =`{'status': ${response.status}, 'statusText': ${response.statusText}}, 'body': ${JSON.stringify(errorData.error)}}`
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
        const errorMessage =`Error updating phone call event: ${error instanceof Error ? error.message : String(error)}`
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