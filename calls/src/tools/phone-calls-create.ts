import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsCreateToolName = "phone-calls-create";
export const phonecallsCreateToolDescription = "create a phone call based on the input arguments";

// Tool Schema
export const PhonecallsCreateToolSchema = z.object({
    userId: z.string().describe("Id of the User on behalf of whom the phone call is made. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    type: z.enum(["simple", "conferenceInvite", "callback"]).describe("The type of the call."),
    //query params
    waitForPickup: z.string().optional().describe("The maximum number of seconds to wait until one of the phone numbers used picks up.When the time value set here runs out, the call is cancelled."),
    callDuration: z.string().optional().describe("Total duration of the call, in seconds."),
    allowPublicTransfer: z.boolean().optional().describe("This flag restricts or permits transfer of a phone call made to a phone number external to the system.This flag is ignored for phone calls made to a local number."),
    video: z.boolean().optional().describe("Enable video support in SDP."),
    number: z.string().optional().describe("Represents the number of the scheduled conference to which the destination is invited."),
    pin: z.string().optional().describe("Represents the PIN of the scheduled conference to which the destination is invited to."),
    //payload params
    extension: z.string().optional().describe("Must refer to a Phone Terminal type Extension. Must be owned by the User identified by the userId sent in the URI-Fragment."),
    source: z.array(z.string()).optional().describe("Can be set to a list of extension numbers or public numbers."),
    destination: z.array(z.string()).optional().describe("Can be any extension number or a public number."),
    callerId: z.string().optional().describe("The caller name and number. It is displayed to the source."),
    callerDestination: z.string().optional().describe("The caller name and number. It is displayed to the destination."),
    nonce: z.string().optional().describe("A unique string which allows to identify the call created based on the request.").default(utils.generateNonce()),
}).strict();

// Tool definition
export const PHONECALLS_CREATE_TOOL: Tool = {
    name: phonecallsCreateToolName,
    description: phonecallsCreateToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsCreateToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsCreateTool(
    args: z.infer<typeof PhonecallsCreateToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; agent?: any; },
    logger: Logger,
) {
    const { type, userId, waitForPickup, callDuration, allowPublicTransfer, video, number, pin, extension, source, destination, callerId, callerDestination, nonce } = PhonecallsCreateToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsCreateToolName} tool...`);
        var paramsPhoneCreateCallURL = '';
        const paramsPhoneCreateCall = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        let payload = {};
        const errors: string[] = [];

        // Check if the values are valid
        if (extension && !utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }
        if (callerId && !utils.validateCallerID(callerId)) {
            errors.push(`callerID: ${utils.errorMessageCallerID}`);
        }
        if (callerDestination && !utils.validateCallerID(callerDestination)) {
            errors.push(`callerDestination: ${utils.errorMessageCallerID}`);
        }
        if (source && source.some(sourceValue => !utils.validatePhoneNumberOrExtension(sourceValue))) {
            errors.push(`source: ${utils.errorMessagePhoneNumberOrExtension}`);
        }
        if (destination && destination.some(destinationValue => !utils.validatePhoneNumberOrExtension(destinationValue))) {
            errors.push(`destination: ${utils.errorMessagePhoneNumberOrExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }

        // Handle path parameter for calls
        paramsPhoneCreateCallURL = paramsPhoneCreateCallURL.concat(
            modifiedUserId && type ? `${modifiedUserId}/${type}/` : '',
        );

        switch (type) {
            case "simple":
                queryParams = [
                    { name: 'waitForPickup', value: waitForPickup },
                    { name: 'callDuration', value: callDuration },
                    { name: 'allowPublicTransfer', value: allowPublicTransfer },
                    { name: 'video', value: video },
                ]
                payload = {
                    extension: extension,
                    phoneCallView: [
                        {
                            source: source,
                            destination: destination,
                            callerId: callerId,
                            callerDestination: callerDestination,
                        }
                    ],
                    nonce: nonce,
                }
                break;
            case "conferenceInvite":
                queryParams = [
                    { name: 'waitForPickup', value: waitForPickup },
                    { name: 'number', value: number },
                    { name: 'pin', value: pin },
                ]
                payload = {
                    extension: extension,
                    phoneCallView: [
                        {
                            source: source,
                            destination: destination,
                            callerId: callerId,
                        }
                    ],
                }
                break;
            case "callback":
                queryParams = [
                    { name: 'waitForPickup', value: waitForPickup },
                    { name: 'callDuration', value: callDuration },
                ]
                payload = {
                    extension: extension,
                    phoneCallView: [
                        {
                            source: source,
                            destination: destination,
                            callerId: callerId,
                        }
                    ],
                    nonce: nonce,
                }
                break;
            default:
                throw new Error(`Invalid call type: ${type}`);
        }

        for (const param of queryParams) {
            if (param.value) {
                if (param.validate) param.validate(param.value);
                paramsPhoneCreateCall.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsPhoneCreateCall.size > 0) {
            paramsPhoneCreateCallURL = paramsPhoneCreateCallURL.concat(`?${paramsPhoneCreateCall}`);
        }

        logger.debug(`Creating ${type} type call from ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneCreateCallURL}`);
        logger.debug(`Payload: ${JSON.stringify(payload)}`);
        const response = await utils.secureAwareFetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneCreateCallURL}`), {
            method: 'POST',
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
        const errorMessage = `Error creating phone call for ${type} type call: ${error instanceof Error ? error.message : String(error)}`
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