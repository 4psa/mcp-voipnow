import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

export const phonecallsUpdateStartStopRecordingToolName = "phone-calls-update-start-stop-recording";
export const phonecallsUpdateStartStopRecordingToolDescription = "This method allows to 'start a recording of'/'stops the recording of' a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateStartStopRecordingToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the Extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCallId can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request."),
    //payload common params
    action: z.enum(["StartRecording", "StopRecording"]).describe("The action to be performed on the phone call."),
    phoneCallViewId: z.string().describe("The PhoneCallView that is subject to the update."),
    //payload start recording params
    format: z.enum(["wav", "wav49"]).describe("The recording format.").default("wav"),
}).strict();


// Tool definition
export const PHONECALLS_UPDATE_START_STOP_RECORDING_TOOL: Tool = {
    name: phonecallsUpdateStartStopRecordingToolName,
    description: phonecallsUpdateStartStopRecordingToolDescription,
    inputSchema: zodToJsonSchema(PhonecallsUpdateStartStopRecordingToolSchema) as ToolInput,
}

export async function runPhonecallsUpdateStartStopRecordingTool(
    args: z.infer<typeof PhonecallsUpdateStartStopRecordingToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, phoneCallViewId, format } = PhonecallsUpdateStartStopRecordingToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateStartStopRecordingToolName} tool...`);
        var paramsPhoneUpdateStartStopRecordingCallURL = '';
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
        paramsPhoneUpdateStartStopRecordingCallURL = paramsPhoneUpdateStartStopRecordingCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        switch (action) {
            case "StartRecording":
                payload = {
                    action: action,
                    phoneCallViewId: phoneCallViewId,
                    format: format,
                };
                break;
            case "StopRecording":
                payload = {
                    action: action,
                    phoneCallViewId: phoneCallViewId,
                };
                break;
            default:
                throw new Error(`Invalid call action: ${action}. Supported actions: StartRecording, StopRecording.`);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateStartStopRecordingCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateStartStopRecordingCallURL}`), {
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