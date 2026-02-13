import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";
import { readFile } from "fs/promises";
import { basename } from "path";


export const faxesCreateToolName = "faxes-create";
export const faxesCreateToolDescription = "Allows uses to send faxes in particular contexts such as User, Organization or global.";

// Tool Schema
export const FaxesCreateToolSchema = z.object({
    userId: z.string().describe("Id of the User on behalf of whom the Fax is sent. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension sending the Fax. Cannot be set to @self."),
    // payload
    recipients: z.array(z.string()).describe("The recipients of the Fax. The numbers may be extended or short (in case of Phone Terminal extensions)."),
    filePath: z.string().describe("The path to the file to be sent."),
}).strict();

// Tool definition
export const FAXES_CREATE_TOOL: Tool = {
    name: faxesCreateToolName,
    description: faxesCreateToolDescription,
    inputSchema: toJsonSchemaCompat(FaxesCreateToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runFaxesCreateTool(
    args: z.infer<typeof FaxesCreateToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, recipients, filePath } = FaxesCreateToolSchema.parse(args);
    try {
        logger.info(`Running ${faxesCreateToolName} tool...`);
        var paramsFaxesCreateURL = '';
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension) || extension === '@self') {
            if (extension === '@self') {
                errors.push(`extension: ${utils.errorMessageExtensionSelf}`);
            } else {
                errors.push(`extension: ${utils.errorMessageExtension}`);
            }
        }
        if (recipients && recipients.some(recipient => !utils.validateExtension(recipient))) {
            errors.push(`recipients: ${utils.errorMessageExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for extensions
        paramsFaxesCreateURL = paramsFaxesCreateURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}` : ''
        );

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        // Create FormData for file upload
        const formData = new FormData();
        
        // Add file (required field)
        const fileBuffer = await readFile(filePath!);
        const fileName = basename(filePath!);
        const blob = new Blob([fileBuffer], { type: 'application/octet-stream' });
        formData.append('files', blob, fileName);

        // Add recipients as JSON in the request field (required field)
        formData.append('request', JSON.stringify({ recipients }));

        logger.debug(`Creating faxes for ${config.voipnowUrl}/uapi/faxes/${paramsFaxesCreateURL}`);
        logger.debug(`FormData fields: ${Array.from(formData.keys()).join(', ')}`);
        logger.debug(`Recipients: ${JSON.stringify(recipients)}`);
        logger.debug(`File: ${fileName} (${fileBuffer.length} bytes)`);
        const response = await utils.secureAwareFetch(utils.createUrl(config.voipnowUrl, `/uapi/faxes/${paramsFaxesCreateURL}`), {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${config.voipnowToken}`,
                "User-Agent": userAgent.toString(),
            },
            body: formData,
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
        const errorMessage = `Error creating faxes: ${error instanceof Error ? error.message : String(error)}`
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