import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const extensionsQueueAgentsUpdateToolName = "extensions-queue-agents-update";
export const extensionsQueueAgentsUpdateToolDescription = "Query allows updating the statuses of agents that are registered to a queue in particular contexts such as User, Organization or global.";

// Tool Schema
export const ExtensionsQueueAgentsUpdateToolSchema = z.object({
    userId: z.string().describe("Id of the User which owns the queue. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Queue Extension. Cannot be set to @self."),
    agent: z.string().describe("Identifier of the queue agent.This can be set to an extension number if the agent is local or an Id for remote agents."),
    //payload params
    status: z.enum(["0","1","2"]).describe("The status of the agent. Possible values: 0-Logged Out, 1-Online, 2-Paused"),
}).strict();

// Tool definition
export const EXTENSIONS_QUEUE_AGENTS_UPDATE_TOOL: Tool = {
    name: extensionsQueueAgentsUpdateToolName,
    description: extensionsQueueAgentsUpdateToolDescription,
    inputSchema: toJsonSchemaCompat(ExtensionsQueueAgentsUpdateToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runExtensionsQueueAgentsUpdateTool(
    args: z.infer<typeof ExtensionsQueueAgentsUpdateToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, agent, status } = ExtensionsQueueAgentsUpdateToolSchema.parse(args);
    try {
        logger.info(`Running ${extensionsQueueAgentsUpdateToolName} tool...`);
        var paramsExtensionsQueueAgentsUpdateURL = '';
        let payload = {};
        const errors: string[] = [];
        
        // Check if the values are valid
        if (!utils.validateExtension(extension) || extension === '@self') {
            if (extension === '@self') {
                errors.push(`extension: ${utils.errorMessageExtensionSelf}`);
            } else {
                errors.push(`extension: ${utils.errorMessageExtension}`);
            }
        }
        if (!utils.validateAgentID(agent)) {
            errors.push(`agent: ${utils.errorMessageAgentID}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsExtensionsQueueAgentsUpdateURL = paramsExtensionsQueueAgentsUpdateURL.concat(
            modifiedUserId && extension && agent ? `${modifiedUserId}/${extension}/queue/agents/${agent}/` : ''
        );

        payload = {
            status: status,
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage =`Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating extensions queue agent with ${status} for ${config.voipnowUrl}/uapi/extensions/${paramsExtensionsQueueAgentsUpdateURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(config.voipnowUrl, `/uapi/extensions/${paramsExtensionsQueueAgentsUpdateURL}`), {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "User-Agent": userAgent.toString(),
                "Authorization": `Bearer ${config.voipnowToken}`,
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
        const errorMessage = `Error updating extensions queue agents: ${error instanceof Error ? error.message : String(error)}`
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