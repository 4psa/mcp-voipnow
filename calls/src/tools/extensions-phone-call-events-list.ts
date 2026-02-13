import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const extensionsPhoneCallEventsListToolName = "extensions-phone-call-events-list";
export const extensionsPhoneCallEventsListToolDescription = "Allows listing phone call events in particular contexts such as User, Organization or global.";

// Tool Schema
export const ExtensionsPhoneCallEventsListToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the Extension for which the event is listed. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension for which the event is listed. Allowed Extension types: Phone Terminal, Queue, Conference, and IVR. Cannot be set to @self."),
    eventType: z.enum(["0", "1", "2", "3", "4"]).optional().describe("Type of the Phone Call Event. If missing events for all the types are returned. Possible values: 0 - Dial-In, 1 - Dial-Out, 2 - Hangup, 3 - Answer incoming call, 4 - Answer outgoing call."),
    eventID: z.string().optional().describe("The Id of the phone call event to be updated."),
    //query params
    count: z.string().optional().describe("The size of the chunk to retrieve.").default("20"),
    filterBy: z.enum(["id", "method", "modified", "note", "status", "type", "url"]).optional().describe("Records can be filtered by all fields of the PhoneCallEvent (http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecallevents-Service.html) ."),
    filterValue: z.string().optional().describe("The value to filter by."),
    startIndex: z.string().optional().describe("The start index of the paged collection.").default("0"),
    fields: z.array(z.string()).optional().describe("An array of Phone Call Event field names. For standard values, please see the PhoneCallEvent (http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecallevents-Service.html) resource."),
    sortOrder: z.enum(["ascending","descending"]).optional().describe("Records will be ordered by url.")
}).strict();

// Tool definition
export const EXTENSIONS_PHONE_CALL_EVENTS_LIST_TOOL: Tool = {
    name: extensionsPhoneCallEventsListToolName,
    description: extensionsPhoneCallEventsListToolDescription,
    inputSchema: toJsonSchemaCompat(ExtensionsPhoneCallEventsListToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runExtensionsPhoneCallEventsListTool(
    args: z.infer<typeof ExtensionsPhoneCallEventsListToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, eventType, eventID, count, filterBy, filterValue, startIndex, fields, sortOrder } = ExtensionsPhoneCallEventsListToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsPhoneCallEventsListToolName} tool...`);
        var paramsExtensionsPhoneCallEventsListURL = '';
        const paramsExtensionsPhoneCallEventsList = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Check eventID
        if (eventID && !eventType) throw Error("eventID can only be used in combination with eventType");

        // Check extension format
        if (!utils.validateExtension(extension) || extension === '@self') {
            if (extension === '@self') {
                errors.push(`extension: ${utils.errorMessageExtensionSelf}`);
            } else {
                errors.push(`extension: ${utils.errorMessageExtension}`);
            }
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsExtensionsPhoneCallEventsListURL = paramsExtensionsPhoneCallEventsListURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/phoneCallEvents/` : '',
            eventType ? `${eventType}/` : '',
            eventID ? `${eventID}/` : ''
        );

        queryParams = [
            { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
            { name: 'filterBy', value: filterBy },
            { name: 'filterValue', value: filterValue },
            { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
            { name: 'fields', value: fields?.join(',') },
            { name: 'sortOder', value: sortOrder }
        ];

        // Handle all query parameters in a single loop
        for (const param of queryParams) {
            if (param.value) {
                if (param.validate && !param.validate(param.value)) {
                    errors.push(`${param.name}: ${param.errorMessage}` || `Validation failed for ${param.name}`);
                };
                paramsExtensionsPhoneCallEventsList.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsExtensionsPhoneCallEventsList.size > 0) {
            paramsExtensionsPhoneCallEventsListURL = paramsExtensionsPhoneCallEventsListURL.concat(`?${paramsExtensionsPhoneCallEventsList}`);
        }

        logger.debug(`Listing phone call events for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsPhoneCallEventsListURL}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/extensions/${paramsExtensionsPhoneCallEventsListURL}`), {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "User-Agent": userAgent.toString(),
                "Authorization": `Bearer ${config.voipnowToken}`,
            },
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
        const errorMessage = `Error listing phone call event: ${error instanceof Error ? error.message : String(error)}`
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