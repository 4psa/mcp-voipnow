import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const extensionsQueueAgentsListToolName = "extensions-queue-agents-list";
export const extensionsQueueAgentsListToolDescription = "Query allows listing all the agents that are registered to a queue in particular contexts such as User, Organization or global.";

// Tool Schema
export const ExtensionsQueueAgentsListToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the queue. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Queue Extension. Cannot be set to @self."),
    agent: z.string().optional().describe("Identifier of the queue agent.This can be set to an extension number if the agent is local or an Id for remote agents."),
    //query params
    count: z.string().optional().describe("The size of the chunk to retrieve.").default("20"),
    filterBy: z.enum(["agentNumber", "queue", "status"]).optional().describe("Records can be filtered only by the following properties: agentNumber, status, queue"),
    filterOp: z.enum(["contains", "equals", "present", "startsWith"]).optional().describe("The parameter must be set to one of the values: contains, equals, present, startsWith"),
    filterValue: z.string().optional().describe("The value to filter by."),
    startIndex: z.string().optional().describe("The start index of the paged collection.").default("0"),
    fields: z.array(z.string()).optional().describe("An array of Phone Call Event field names. For standard values, please see the Agent resource(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Queueagents-Service.html)."),
    sortOrder: z.enum(["ascending","descending"]).optional().describe("Records will be ordered by status.")
}).strict();

// Tool definition
export const EXTENSIONS_QUEUE_AGENTS_LIST_TOOL: Tool = {
    name: extensionsQueueAgentsListToolName,
    description: extensionsQueueAgentsListToolDescription,
    inputSchema: toJsonSchemaCompat(ExtensionsQueueAgentsListToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runExtensionsQueueAgentsListTool(
    args: z.infer<typeof ExtensionsQueueAgentsListToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, agent, count, filterBy, filterOp, filterValue, startIndex, fields, sortOrder } = ExtensionsQueueAgentsListToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsQueueAgentsListToolName} tool...`);
        var paramsExtensionsQueueAgentsListURL = '';
        const paramsExtensionsQueueAgentsList = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension) || extension === '@self') {
            if (extension === '@self') {
                errors.push(`extension: ${utils.errorMessageExtensionSelf}`);
            } else {
                errors.push(`extension: ${utils.errorMessageExtension}`);
            }
        }
        if (agent && !utils.validateAgentID(agent)) {
            errors.push(`agent: ${utils.errorMessageAgentID}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsExtensionsQueueAgentsListURL = paramsExtensionsQueueAgentsListURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/queue/agents/` : '',
            agent ? `${agent}/` : ''
        );

        queryParams = [
            { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
            { name: 'filterBy', value: filterBy },
            { name: 'filterOp', value: filterOp },
            { name: 'filterValue', value: filterValue },
            { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
            { name: 'fields', value: fields },
            { name: 'sortOrder', value: sortOrder },
        ];

        // Handle all query parameters in a single loop
        for (const param of queryParams) {
            if (param.value) {
                if (param.validate && !param.validate(param.value)) {
                    errors.push(`${param.name}: ${param.errorMessage}` || `Validation failed for ${param.name}`);
                };
                paramsExtensionsQueueAgentsList.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsExtensionsQueueAgentsList.size > 0) {
            paramsExtensionsQueueAgentsListURL = paramsExtensionsQueueAgentsListURL.concat(`?${paramsExtensionsQueueAgentsList}`);
        }

        logger.debug(`Listing extensions queue agents for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsQueueAgentsListURL}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/extensions/${paramsExtensionsQueueAgentsListURL}`), {
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
        const errorMessage = `Error listing extensions queue agents: ${error instanceof Error ? error.message : String(error)}`
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