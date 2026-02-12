import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsUpdatePickupBargeinToolName = "phone-calls-update-pickup-bargein";
export const phonecallsUpdatePickupBargeinToolDescription = "This method allows to 'pick up'/'barge in on' a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdatePickupBargeinToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request."),
    //payload common params
    action: z.enum(["PickUp", "BargeIn"]).describe("The action to be performed on the phone call."),
    sendCallTo: z.string().describe("PickUp: Number of the Extension that connects to the parked phone call; BargeIn: Number of the extension that will barge in. Must be in the same Organization as the Extension given in the URI-Fragment."),
    callerId: z.string().optional().describe("The caller name and number. It is displayed to the source. Default: the callerId of the Phone Terminal Extension"),
    waitForPickup: z.string().optional().describe("The maximum number of seconds to wait until one of the phone numbers used picks up. When the time value set here runs out, the call is cancelled.").default("25"),
    phoneCallViewId: z.string().describe("The PhoneCallView that is subject to the update."),
}).strict();


// Tool definition
export const PHONECALLS_UPDATE_PICKUP_BARGEIN_TOOL: Tool = {
    name: phonecallsUpdatePickupBargeinToolName,
    description: phonecallsUpdatePickupBargeinToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsUpdatePickupBargeinToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsUpdatePickupBargeinTool(
    args: z.infer<typeof PhonecallsUpdatePickupBargeinToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, phoneCallViewId, sendCallTo, callerId, waitForPickup } = PhonecallsUpdatePickupBargeinToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdatePickupBargeinToolName} tool...`);
        var paramsPhoneUpdatePickupBargeinCallURL = '';
        let payload = {};
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }
        if (!utils.validateExtension(sendCallTo)) {
            errors.push(`sendCallTo: ${utils.errorMessageExtension}`);
        }
        if (callerId && !utils.validateCallerID(callerId)) {
            errors.push(`callerId: ${utils.errorMessageCallerID}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneUpdatePickupBargeinCallURL = paramsPhoneUpdatePickupBargeinCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            phoneCallViewId: phoneCallViewId,
            sendCallTo: sendCallTo,
            callerId: callerId,
            waitForPickup: waitForPickup,
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage =`Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdatePickupBargeinCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdatePickupBargeinCallURL}`), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': userAgent.toString(),
                'Authorization': `Bearer ${config.voipnowToken}`
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