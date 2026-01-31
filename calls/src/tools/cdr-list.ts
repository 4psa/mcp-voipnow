import { z } from "zod";
import * as utils from "../utils.js";
import { Tool, ToolSchema } from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";
import { Logger } from "winston";

const ToolInputSchema = ToolSchema.shape.inputSchema;
type ToolInput = z.infer<typeof ToolInputSchema>;

export const cdrListToolName = "cdr-list";
export const cdrListToolDescription = "Query call history records with filtering options";

// Tool Schema
export const CDRListToolSchema = z.object({
    ownerId: z.string().optional().describe("Filter phone call history records based on the owner of the call history."),
    count: z.string().optional().describe("The size of the chunk to retrieve.").default("20"),
    filterBy: z.enum(["source", "destination", "published", "answered"]).optional().describe("Filter phone call history records based on their source, destination, published or answered time."),
    filterValue: z.string().optional().describe("Filter phone call history records based on their source, destination, published or answered time."),
    source: z.string().optional().describe("The number that made the call. Can be an extended extension number or a public phone number."),
    destination: z.string().optional().describe("The number that received the call. Can be an extended extension number or a public phone number."),
    startDate: z.string().datetime({ local: true }).optional().describe("Date when the call was answered (Default: first day of the current month). EG: '2024-10-05T00:00:00'"),
    endDate: z.string().datetime({ local: true }).optional().describe("Date when the call was answered (Default: current time). EG: '2024-10-05T00:00:00'"),
    saveStartDate: z.string().datetime({ local: true }).optional().describe("Date when the call was saved to the database. EG: 2024-10-05T00:00:00"),
    saveEndDate: z.string().datetime({ local: true }).optional().describe("Date when the call was saved to the database. EG: 2024-10-05T00:00:00"),
    disposition: z.enum(["0", "1", "2", "3", "4", "5"]).optional().describe(`The call disposition:
      0 - ANSWERED - to fetch calls that were answered;
      1 - BUSY - to get the calls that were answered with a busy tone 
      2 - FAILED - to fetch the calls that have failed 
      3 - NO ANSWER - to fetch the calls that had no answer 
      4 - UNKNOWN - to fetch the unknown calls 
      5 - NOT ALLOWED - to fetch the calls that were not allowed.`),
    flow: z.enum(["2", "4", "8"]).optional().describe(`The flow of the call, which is set to:
      2 - a local call
      4 - an outgoing public call
      8 - an incoming public call`),
    fields: z.array(z.string()).optional().describe("An array of PhoneCallStat (https://wiki.4psa.com/VoipNow/Developer-Guide/UnifiedAPI-v5/Cdr-Service.html) field names."),
    startIndex: z.string().optional().describe("The start index of the paged collection.").default("0"),
    sortOrder: z.enum(["ascending","descending"]).optional().describe("Records will be ordered by published.")
}).strict();

// Tool definition
export const CDR_LIST_TOOL: Tool = {
    name: cdrListToolName,
    description: cdrListToolDescription,
    inputSchema: zodToJsonSchema(CDRListToolSchema) as ToolInput,
}

export async function runCDRListTool(
    args: z.infer<typeof CDRListToolSchema>,
    userAgent: string,
    config: { voipnowUrl: string; voipnowToken: string; },
    logger: Logger,
) {
    const { ownerId, count, filterBy, filterValue, source, destination, startDate, endDate, saveStartDate, saveEndDate, disposition, flow, fields, startIndex, sortOrder } = CDRListToolSchema.parse(args);
    try {
        logger.info(`Running ${cdrListToolName} tool...`);
        var paramsCallHistoryURL = '';
        const paramsCallHistory = new URLSearchParams();
        let queryParams: utils.QueryParam[] = [];
        const errors: string[] = [];

        // Handle path parameter for cdr
        paramsCallHistoryURL = paramsCallHistoryURL.concat(
            ownerId ? `${ownerId}/` : ''
        );

        queryParams = [
            { name: 'count', value: count, validate: utils.validateCount, errorMessage: utils.errorMessageCount },
            { name: 'filterBy', value: filterBy },
            { name: 'filterValue', value: filterValue },
            { name: 'source', value: source, validate: utils.validatePhoneNumberOrExtension, errorMessage: utils.errorMessagePhoneNumberOrExtension },
            { name: 'destination', value: destination, validate: utils.validatePhoneNumberOrExtension, errorMessage: utils.errorMessagePhoneNumberOrExtension },
            { name: 'startDate', value: startDate },
            { name: 'endDate', value: endDate },
            { name: 'saveStartDate', value: saveStartDate },
            { name: 'saveEndDate', value: saveEndDate },
            { name: 'disposition', value: disposition },
            { name: 'flow', value: flow },
            { name: 'fields', value: fields?.join(',') },
            { name: 'startIndex', value: startIndex, validate: utils.validateStartIndex, errorMessage: utils.errorStartIndex },
            { name: 'sortOrder', value: sortOrder },
        ];

        // Handle all query parameters in a single loop
        for (const param of queryParams) {
            if (param.value) {
                if (param.validate && !param.validate(param.value)) {
                    errors.push(`${param.name}: ${param.errorMessage}` || `Validation failed for ${param.name}`);
                };
                paramsCallHistory.append(param.name, param.value);
            }
        }

        if (paramsCallHistory.size > 0) {
            paramsCallHistoryURL = paramsCallHistoryURL.concat(`?${paramsCallHistory}`);
        }

        // Throw an error if there are any validation errors
        if (errors.length > 0) {
            const errorMessage = `Error validating query parameters: ${errors.join('; ')}`
            throw new Error(errorMessage);
        }

        logger.debug(`Fetching phone call records info from ${config.voipnowUrl}/uapi/cdr/${paramsCallHistoryURL}`);
        const response = await fetch(utils.createUrl(`${config.voipnowUrl}`, `/uapi/cdr/${paramsCallHistoryURL}`), {
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
        const errorMessage = `Error fetching phone call records info: ${error instanceof Error ? error.message : String(error)}`
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