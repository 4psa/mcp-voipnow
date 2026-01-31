import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

const PhonecallsUpdateParkUnparkCommonToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call. Use @self to match all the extensions under the User."),
    phoneCallId: z.string().describe("The Id of the phone call to be updated. If the Extension is unknown, you can use @self and phoneCallId to identify the phone call. The PhoneCall Id can be retrieved using the List PhoneCalls(http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html#list-phonecalls) request. For 'Park': If not provided, all phone calls owned by Extension are parked. For 'UnPark': If not provided, all phone calls owned by Extension are retrieved from the parking lot."),
    //payload common params
    phoneCallViewId: z.string().describe("The PhoneCallView that is subject to the update."),
});

export const phonecallsUpdateParkToolName = "phone-calls-update-park";
export const phonecallsUpdateParkToolDescription = "This method allows to park a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateParkToolSchema = PhonecallsUpdateParkUnparkCommonToolSchema.extend({
    action: z.enum(["Park"]).describe("The action to be performed on the phone call."),
    //payload park params
    maxInParking: z.number().optional().describe("The time interval during which the call stays in the parking lot. When the time runs out, the phone call is picked up from the parking lot by the Extension that put it there.").default(180).refine((value) => value >= 10 && value <= 3600, { message: "maxInParking must be between 10 and 3600." }),
}).strict();

// Tool definition
export const PHONECALLS_UPDATE_PARK_TOOL: Tool = {
    name: phonecallsUpdateParkToolName,
    description: phonecallsUpdateParkToolDescription,
    inputSchema: zodToJsonSchema(PhonecallsUpdateParkToolSchema) as ToolInput,
}

export async function runPhonecallsUpdateParkTool(
    args: z.infer<typeof PhonecallsUpdateParkToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, phoneCallViewId, maxInParking } = PhonecallsUpdateParkToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateParkToolName} tool...`);
        var paramsPhoneUpdateParkCallURL = '';
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
        paramsPhoneUpdateParkCallURL = paramsPhoneUpdateParkCallURL.concat(
            modifiedUserId && extension && phoneCallId ? `${modifiedUserId}/${extension}/${phoneCallId}/` : ''
        );

        payload = {
            action: action,
            phoneCallViewId: phoneCallViewId,
            maxInParking: maxInParking,
        };

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateParkCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateParkCallURL}`), {
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

export const phonecallsUpdateUnparkToolName = "phone-calls-update-unpark";
export const phonecallsUpdateUnparkToolDescription = "This method allows to retrieve from parking lot a phone call in particular contexts such as User, Organization or global. ";

// Tool Schema
export const PhonecallsUpdateUnparkToolSchema = PhonecallsUpdateParkUnparkCommonToolSchema.extend({
    action: z.enum(["UnPark"]).describe("The action to be performed on the phone call."),
    //payload unpark params
    sendCallTo: z.string().describe("Number of the Extension that connects to the parked phone call. Must refer to a Phone Terminal Extension."),
    callerId: z.string().optional().describe("The caller name and number. It is displayed to the source. Default: the caller Id of the Phone Terminal Extension."),
    waitForPickup: z.string().optional().describe("The maximum number of seconds to wait until one of the phone numbers used picks up. When the time value set here runs out, the call is cancelled.").default("25"),
}).strict();

// Tool definition
export const PHONECALLS_UPDATE_UNPARK_TOOL: Tool = {
    name: phonecallsUpdateUnparkToolName,
    description: phonecallsUpdateUnparkToolDescription,
    inputSchema: zodToJsonSchema(PhonecallsUpdateUnparkToolSchema) as ToolInput,
}

export async function runPhonecallsUpdateUnparkTool(
    args: z.infer<typeof PhonecallsUpdateUnparkToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, action, phoneCallViewId, sendCallTo, callerId, waitForPickup } = PhonecallsUpdateUnparkToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsUpdateUnparkToolName} tool...`);
        var paramsPhoneUpdateUnparkCallURL = '';
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
        paramsPhoneUpdateUnparkCallURL = paramsPhoneUpdateUnparkCallURL.concat(
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
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Updating phone call with ${action} for ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneUpdateUnparkCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneUpdateUnparkCallURL}`), {
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