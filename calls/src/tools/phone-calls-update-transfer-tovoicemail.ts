import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


const PhonecallsUpdateTransferTovoicemailCommonToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request."),
    //payload common params
    sendCallTo: z.string().describe("Phone number where the call is transferred. Can be an extension number or a public number. Must refer to a Phone Terminal type Extension."),
});

export const phonecallsUpdateTransferToolName = "phone-calls-update-transfer";
export const phonecallsUpdateTransferToolDescription = "This method allows to transfer a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateTransferToolSchema = PhonecallsUpdateTransferTovoicemailCommonToolSchema.extend({
    action: z.enum(["Transfer"]).describe("The action to be performed on the phone call."),
    transferFromNumber: z.string().describe("The phone number of the party that transfers the call. Its value can be the phone number of the source or destination"),
    transferNumber: z.string().optional().describe("The phone number of the party being transferred. Its value can be the phone number of the source or destination."),
}).strict();

// Tool definition
export const PHONECALLS_UPDATE_TRANSFER_TOOL: Tool = {
    name: phonecallsUpdateTransferToolName,
    description: phonecallsUpdateTransferToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsUpdateTransferToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsUpdateTransferTool(
    args: z.infer<typeof PhonecallsUpdateTransferToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, sendCallTo, transferFromNumber, transferNumber } = PhonecallsUpdateTransferToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateTransferToolName} tool...`);
        var paramsPhoneUpdateTransferCallURL = '';
        let payload = {};
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }
        if (!utils.validatePhoneNumberOrExtension(sendCallTo)) {
            errors.push(`sendCallTo: ${utils.errorMessagePhoneNumberOrExtension}`);
        }
        if (!utils.validatePhoneNumberOrExtension(transferFromNumber)) {
            errors.push(`transferFromNumber: ${utils.errorMessagePhoneNumberOrExtension}`);
        }
        if (transferNumber && !utils.validatePhoneNumberOrExtension(transferNumber)) {
            errors.push(`transferNumber: ${utils.errorMessagePhoneNumberOrExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneUpdateTransferCallURL = paramsPhoneUpdateTransferCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            sendCallTo: sendCallTo,
            transferFromNumber: transferFromNumber,
            transferNumber: transferNumber,
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }
        
        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateTransferCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateTransferCallURL}`), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': userAgent.toString(),
                'Authorization': `Bearer ${config.voipnowToken}`
            },
            body: JSON.stringify(payload),
            redirect: 'manual', // Prevent automatic redirection
            ...(config.agent && { agent: config.agent }),
        });

        // Handle non-2xx responses
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 400 || response.status === 401 || response.status === 403 || response.status === 500) {
                const errorMessage =`{'code': ${errorData.error.code}, 'message': ${errorData.error.message}}`
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
        const errorMessage =`Error updating phone call for ${action}: ${error instanceof Error ? error.message : String(error)}`
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

export const phonecallsUpdateTransferTovoicemailToolName = "phone-calls-update-transfer-tovoicemail";
export const phonecallsUpdateTransferTovoicemailToolDescription = "This method allows to transfer to voicemail a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateTransferTovoicemailToolSchema = PhonecallsUpdateTransferTovoicemailCommonToolSchema.extend({
    action: z.enum(["TransferToVoicemail"]).describe("The action to be performed on the phone call."),
    transferFromNumber: z.string().optional().describe("The phone number of the party that transfers the call. Its value can be the phone number of the source or destination"),
    transferNumber: z.string().describe("The phone number of the party being transferred. Its value can be the phone number of the source or destination."),
}).strict();

// Tool definition
export const PHONECALLS_UPDATE_TRANSFER_TOVOICEMAIL_TOOL: Tool = {
    name: phonecallsUpdateTransferTovoicemailToolName,
    description: phonecallsUpdateTransferTovoicemailToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsUpdateTransferTovoicemailToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsUpdateTransferTovoicemailTool(
    args: z.infer<typeof PhonecallsUpdateTransferTovoicemailToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, sendCallTo, transferFromNumber, transferNumber } = PhonecallsUpdateTransferTovoicemailToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateTransferTovoicemailToolName} tool...`);
        var paramsPhoneUpdateTransferTovoicemailCallURL = '';
        let payload = {};
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }
        if (!utils.validateExtension(sendCallTo)) {
            errors.push(`sendCallTo: ${utils.errorMessageExtension}`);
        }
        if (!utils.validatePhoneNumberOrExtension(transferNumber)) {
            errors.push(`transferNumber: ${utils.errorMessagePhoneNumberOrExtension}`);
        }
        if (transferFromNumber && !utils.validatePhoneNumberOrExtension(transferFromNumber)) {
            errors.push(`transferFromNumber: ${utils.errorMessagePhoneNumberOrExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneUpdateTransferTovoicemailCallURL = paramsPhoneUpdateTransferTovoicemailCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            sendCallTo: sendCallTo,
            transferFromNumber: transferFromNumber,
            transferNumber: transferNumber,
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateTransferTovoicemailCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateTransferTovoicemailCallURL}`), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': userAgent.toString(),
                'Authorization': `Bearer ${config.voipnowToken}`
            },
            body: JSON.stringify(payload),
            redirect: 'manual', // Prevent automatic redirection
            ...(config.agent && { agent: config.agent }),
        });

        // Handle non-2xx responses
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 400 || response.status === 401 || response.status === 403 || response.status === 500) {
                const errorMessage = `Error updating phone call for ${action}: {'code': ${errorData.error.code}, 'message': ${errorData.error.message}}`
                throw new Error(errorMessage);
            }
            const errorMessage = `Error updating phone call for ${action}: {'status': ${response.status}, 'statusText': ${response.statusText}}, 'body': ${JSON.stringify(errorData.error)}}`
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
        const errorMessage = `Error updating phone call for ${action}: ${error instanceof Error ? error.message : String(error)}`
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