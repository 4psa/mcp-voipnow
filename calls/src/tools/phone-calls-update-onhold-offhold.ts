import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsUpdateOnholdOffholdToolName = "phone-calls-update-onhold-offhold";
export const phonecallsUpdateOnholdOffholdToolDescription = "This method allows to 'put on hold'/'take off from hold' a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateOnholdOffholdToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated.If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request. For 'OnHold': If not provided, all phone calls owned by the Extension are put on hold"),
    //payload common params
    action: z.enum(["OnHold", "OffHold"]).describe("The action to be performed on the phone call."),
    phoneCallViewId: z.string().describe("The PhoneCallView that is subject to the update."),
}).strict();


// Tool definition
export const PHONECALLS_UPDATE_ONHOLD_OFFHOLD_TOOL: Tool = {
    name: phonecallsUpdateOnholdOffholdToolName,
    description: phonecallsUpdateOnholdOffholdToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsUpdateOnholdOffholdToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsUpdateOnholdOffholdTool(
    args: z.infer<typeof PhonecallsUpdateOnholdOffholdToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, phoneCallViewId } = PhonecallsUpdateOnholdOffholdToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateOnholdOffholdToolName} tool...`);
        var paramsPhoneUpdateOnholdOffholdCallURL = '';
        let payload = {};

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            throw new Error(utils.errorMessageExtension);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneUpdateOnholdOffholdCallURL = paramsPhoneUpdateOnholdOffholdCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            phoneCallViewId: phoneCallViewId
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateOnholdOffholdCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateOnholdOffholdCallURL}`), {
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