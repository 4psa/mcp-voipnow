import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { toJsonSchemaCompat } from "@modelcontextprotocol/sdk/server/zod-json-schema-compat.js";
import { Logger } from "winston";


export const phonecallsListToolName = "phone-calls-list";
export const phonecallsListToolDescription = "This method allows listing of PhoneCalls resources in particular contexts such as User, Organization or global.";

// Tool Schema
export const PhonecallsListToolSchema = z.object({
    userId: z.string().describe("Id of the User that owns the Extension involved in the phone call. Possible values: @me,@viewer,@owner,<user_id>").default("@me"),
    extension: z.string().describe("Number of the Extension involved in the call."),
    phoneCallId: z.string().optional().describe("The Id of the phone call to be updated."),
    //query params
    count: z.string().optional().describe("The size of the chunk to retrieve.").default("20"),
    filterBy: z.enum(["id", "published"]).optional().describe("Records can be filtered by PhoneCall id and published date."),
    filterOp: z.enum(["contains","equals","greaterThan","inArray","lessThan","present","startsWith"]).optional().describe("The parameter must be set to one of the values: equals, greaterThan, lessThan, present, startsWith, contains, inArray."),
    filterValue: z.string().optional().describe("The value to filter by. You can filter by the phone call id or the published date"),
    startIndex: z.string().optional().describe("The start index of the paged collection.").default("0"),
    fields: z.array(z.string()).optional().describe("An array of PhoneCall (http://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Phonecall-Service.html) field names."),
    sortOrder: z.enum(["ascending","descending"]).optional().describe("The records are always ordered by their publish time.")
}).strict();

// Tool definition
export const PHONECALLS_LIST_TOOL: Tool = {
    name: phonecallsListToolName,
    description: phonecallsListToolDescription,
    inputSchema: toJsonSchemaCompat(PhonecallsListToolSchema, { strictUnions: true, pipeStrategy: 'input' }) as any,
}

export async function runPhonecallsListTool(
    args: z.infer<typeof PhonecallsListToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { userId, extension, phoneCallId, count, filterBy, filterOp, filterValue, startIndex, fields, sortOrder } = PhonecallsListToolSchema.parse(args);
    try {
        logger.info(`Running ${phonecallsListToolName} tool...`);
        var paramsPhoneListCallURL = '';
        const paramsPhoneListCall = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Check if the values are valid
        if (!utils.validateExtension(extension)) {
            errors.push(`extension: ${utils.errorMessageExtension}`);
        }

        // Check if userId starts with '@' for some values
        let modifiedUserId = userId;
        if (['me', 'viewer', 'owner'].includes(userId) && !userId.startsWith('@')) {
            modifiedUserId = '@' + userId;
        }
        
        // Handle path parameter for calls
        paramsPhoneListCallURL = paramsPhoneListCallURL.concat(
            modifiedUserId && extension ? `${modifiedUserId}/${extension}/` : '',
            phoneCallId ? `${phoneCallId}/` : ''
        );

        queryParams = [
            { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
            { name: 'filterBy', value: filterBy },
            { name: 'filterOp', value: filterOp },
            { name: 'filterValue', value: filterValue },
            { name: 'fields', value: fields?.join(',') },
            { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
            { name: 'sortOrder', value: sortOrder },
        ];

        for (const param of queryParams) {
            if (param.value) {
                if (param.validate && !param.validate(param.value)){
                    errors.push(`${param.name}: ${param.errorMessage}` || `Validation failed for ${param.name}`);
                };
                paramsPhoneListCall.append(param.name, param.value);
            }
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        if (paramsPhoneListCall.size > 0) {
            paramsPhoneListCallURL = paramsPhoneListCallURL.concat(`?${paramsPhoneListCall}`);
        }

        logger.debug(`Listing phone calls from ${config.voipnowUrl}/uapi/phoneCalls/${paramsPhoneListCallURL}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/phoneCalls/${paramsPhoneListCallURL}`), {
            method: 'GET',
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
        const errorMessage =`Error listing phone calls: ${error instanceof Error ? error.message : String(error)}`
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