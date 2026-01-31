import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

export const extensionsPresenceListToolName = "extensions-presence-list";
export const extensionsPresenceListToolDescription = "Query allows to list the registration status of extensions";

// Tool Schema
export const ExtensionsPresenceListToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the Extensions for which the presence is returned. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Extended number of a Phone Terminal Extension. Use @self to match all the extensions under the User."),
    //query params
    count: z.string().optional().describe("The size of the chunk to retrieve.").default("20"),
    filterBy: z.enum(["extension"]).optional().describe("Records can be filtered only by the extension field."),
    filterOp: z.enum(["contains", "equals", "inArray", "startsWith"]).optional().describe("Records can be filtered only by the extension field."),
    filterValue: z.string().optional().describe("The value to filter by."),
    startIndex: z.string().optional().describe("The start index of the paged collection.").default("0"),
    fields: z.array(z.string()).optional().describe("An array of ExtensionPresence field names. For standard values, please see the Presence (http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Presence-Service.html) object."),
    sortOrder: z.enum(["ascending","descending"]).optional().describe("Records will be ordered by the number of the extension. ")
}).strict();

// Tool definition
export const EXTENSIONS_PRESENCE_LIST_TOOL: Tool = {
    name: extensionsPresenceListToolName,
    description: extensionsPresenceListToolDescription,
    inputSchema: zodToJsonSchema(ExtensionsPresenceListToolSchema) as ToolInput,
}

export async function runExtensionsPresenceListTool(
    args: z.infer<typeof ExtensionsPresenceListToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const {  userId, extension, count, filterBy, filterOp, filterValue, startIndex, fields, sortOrder } = ExtensionsPresenceListToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsPresenceListToolName} tool...`);
        var paramsExtensionsPresenceURL = '';
        const paramsExtensionsPresence = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Check extension format
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsExtensionsPresenceURL = paramsExtensionsPresenceURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/presence/` : ''
        );

        queryParams = [
            { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
            { name: 'filterBy', value: filterBy },
            { name: 'filterOp', value: filterOp },
            { name: 'filterValue', value: filterValue },
            { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
            { name: 'fields', value: fields?.join(',') },
            { name: 'sortOrder', value: sortOrder },
        ];

        // Handle all query parameters in a single loop
        for (const param of queryParams) {
            if (param.value) {
                if (param.validate && !param.validate(param.value)){
                    errors.push(`${param.name}: ${param.errorMessage}` || `Validation failed for ${param.name}`);
                };
                paramsExtensionsPresence.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsExtensionsPresence.size > 0) {
            paramsExtensionsPresenceURL = paramsExtensionsPresenceURL.concat(`?${paramsExtensionsPresence}`);
        }

        logger.debug(`Listing extensions presence for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsPresenceURL}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/extensions/${paramsExtensionsPresenceURL}`), {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "User-Agent": userAgent.toString(),
                "Authorization": `Bearer ${config.voipnowToken}`,
            },
            redirect: 'manual' // Prevent automatic redirection
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
        const errorMessage = `Error listing extensions presence: ${error instanceof Error ? error.message : String(error)}`
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