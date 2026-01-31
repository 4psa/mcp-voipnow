import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

export const phonecallsUpdateMonitorToolName = "phone-calls-update-monitor";
export const phonecallsUpdateMonitorToolDescription = "This method allows monitoring on a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateMonitorToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request."),
    //payload params
    action: z.enum(["Monitor"]).describe("The action to be performed on the phone call."),
    sendCallTo: z.string().describe("Number of the extension that will monitor. Must be in the same Organization as the Extension given in the URI-Fragment. Must refer to a Phone Terminal Extension."),
    callerId: z.string().optional().describe("The caller name and number. It is displayed to the source. Default: the callerId of the Phone Terminal Extension."),
    waitForPickup: z.string().optional().describe("The maximum number of seconds to wait until one of the phone numbers used picks up. When the time value set here runs out, the call is cancelled.").default("25"),
    phoneCallViewId: z.string().describe("The PhoneCallView(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html) that is subject to the update."),
}).strict();


// Tool definition
export const PHONECALLS_UPDATE_MONITOR_TOOL: Tool = {
    name: phonecallsUpdateMonitorToolName,
    description: phonecallsUpdateMonitorToolDescription,
    inputSchema: zodToJsonSchema(PhonecallsUpdateMonitorToolSchema) as ToolInput,
}

export async function runPhonecallsUpdateMonitorTool(
    args: z.infer<typeof PhonecallsUpdateMonitorToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, sendCallTo, callerId, waitForPickup, phoneCallViewId } = PhonecallsUpdateMonitorToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateMonitorToolName} tool...`);
        var paramsPhoneUpdateMonitorCallURL = '';
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
        paramsPhoneUpdateMonitorCallURL = paramsPhoneUpdateMonitorCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            sendCallTo: sendCallTo,
            callerId: callerId,
            waitForPickup: waitForPickup,
            phoneCallViewId: phoneCallViewId
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateMonitorCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateMonitorCallURL}`), {
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