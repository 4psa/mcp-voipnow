import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsDeleteToolName = "phone-calls-delete";
export const phonecallsDeleteToolDescription = "This method allows hanging up PhoneCalls in particular contexts such as User, Organization or global.";

// Tool Schema
export const PhonecallsDeleteToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call."),
    phoneCallId: z.string().optional().describe("The Id of the phone call to be updated."),
    //query params
    phoneNumber: z.string().optional().describe("Phone number of one of the parties involved in the phone call. When given, the number involved in the phone call and the Extension are closed.")
}).strict();

// Tool definition
export const PHONECALLS_DELETE_TOOL: Tool = {
    name: phonecallsDeleteToolName,
    description: phonecallsDeleteToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsDeleteToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsDeleteTool(
    args: z.infer<typeof PhonecallsDeleteToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, phoneNumber } = PhonecallsDeleteToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsDeleteToolName} tool...`);
        var paramsPhoneDeleteCallURL = '';
        const paramsPhoneDeleteCall = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }
        if (phoneNumber && !utils.validatePhoneNumber(phoneNumber)) {
            errors.push(`phoneNumber: ${utils.errorMessagePhoneNumber}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneDeleteCallURL = paramsPhoneDeleteCallURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/` : '',
            phoneCallId ? `${phoneCallId}/` : ''
        );

        queryParams = [
            { name: 'phoneNumber', value: phoneNumber },
        ];

        for (const param of queryParams) {
            if (param.value) {
                if (param.validate) param.validate(param.value);
                paramsPhoneDeleteCall.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsPhoneDeleteCall.size > 0) {
            paramsPhoneDeleteCallURL = paramsPhoneDeleteCallURL.concat(`?${paramsPhoneDeleteCall}`);
        }

        logger.debug(`Deleting phone call from ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneDeleteCallURL}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneDeleteCallURL}`), {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': userAgent.toString(),
                'Authorization': `Bearer ${config.voipnowToken}`
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
        const errorMessage = `Error deleting phone calls: ${error instanceof Error ? error.message : String(error)}`
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