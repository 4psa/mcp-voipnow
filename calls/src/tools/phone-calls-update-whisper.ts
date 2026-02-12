import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsUpdateWhisperToolName = "phone-calls-update-whisper";
export const phonecallsUpdateWhisperToolDescription = "This method allows a third-party to whisper on a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateWhisperToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the Extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request."),
    //payload params
    action: z.enum(["Whisper"]).describe("The action to be performed on the phone call."),
    sendCallTo: z.string().describe("Number of the Extension that connects to the parked phone call. Must refer to a Phone TerminalExtension."),
    callerId: z.string().optional().describe("The caller name and number. It is displayed to the source. Default: the callerId of the Phone Terminal Extension."),
    waitForPickup: z.string().optional().describe("The maximum number of seconds to wait until one of the phone numbers used picks up. When the time value set here runs out, the call is cancelled.").default("25"),
    phoneCallViewId: z.string().describe("The PhoneCallView that is subject to the update."),
    privateW: z.enum(["0", "1"]).optional().describe("When set to 1, the extension that whispers does not hear the conversation between the the parties involved in the call.").default("0"),
}).strict();


// Tool definition
export const PHONECALLS_UPDATE_WHISPER_TOOL: Tool = {
    name: phonecallsUpdateWhisperToolName,
    description: phonecallsUpdateWhisperToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsUpdateWhisperToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsUpdateWhisperTool(
    args: z.infer<typeof PhonecallsUpdateWhisperToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, sendCallTo, callerId, waitForPickup, phoneCallViewId, privateW } = PhonecallsUpdateWhisperToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateWhisperToolName} tool...`);
        var paramsPhoneUpdateWhisperCallURL = '';
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
        paramsPhoneUpdateWhisperCallURL = paramsPhoneUpdateWhisperCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            sendCallTo: sendCallTo,
            callerId: callerId,
            waitForPickup: waitForPickup,
            phoneCallViewId: phoneCallViewId,
            private: privateW,
        };

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateWhisperCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateWhisperCallURL}`), {
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