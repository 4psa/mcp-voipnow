import os
import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from dotenv import load_dotenv

class AIAgent:
    def __init__(self) -> None:
        # Load environment variables
        load_dotenv()
        
        self.client = AsyncOpenAI(
            base_url=os.getenv("OPENAI_BASE_URL"),
            api_key=os.getenv("OPENAI_API_KEY")
        )

    async def generate_tool_call(self, test_type: str, valid_tools: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a tool call for the specified test type"""
        prompts = {
            "create": self._get_create_prompt,
            "hold": self._get_hold_prompt,
            "monitor": self._get_monitor_prompt,
            "park": self._get_park_prompt,
            "record": self._get_record_prompt,
            "transfer": self._get_transfer_prompt,
            "cdr": self._get_cdr_prompt
        }

        prompt_func = prompts.get(test_type)
        if not prompt_func:
            raise ValueError(f"Unknown test type: {test_type}")
            
        prompt = prompt_func(valid_tools, context)

        try:
            response = await self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL"),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error generating tool call from AI: {str(e)}")
            return self._get_fallback_parameters(test_type, context)

    def _get_create_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        test_extension = os.getenv("TEST_EXTENSION")
        test_destination = os.getenv("TEST_DESTINATION")
        
        return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to create a phone call from extension {test_extension} to destination {test_destination}.

Return JSON with:
- tool: the tool name to use
- params: an object with required parameters for a phone call:
  - type: must be "simple" for basic calls
  - source: array with the source extension
  - destination: array with the destination number
  - extension: string with the source extension
  - userId: "@me"
"""

    def _get_hold_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        action = context.get("action", "OnHold")
        return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to {action.lower()} call {context.get('call_id')} for extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-onhold-offhold"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "{action}"
  - phoneCallViewId: string with view ID
"""

    def _get_monitor_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to monitor call {context.get('call_id')} for extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-monitor"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "Monitor"
  - sendCallTo: string with extension number
  - phoneCallViewId: string with view ID
"""

    def _get_park_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        action = context.get('action', 'Park')
        if action == "Park":
            return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to park call {context.get('call_id')} for extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-park"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "Park"
  - phoneCallViewId: string with view ID
  - maxInParking: integer max seconds in parking
"""
        else:
            return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to unpark call {context.get('call_id')} for extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-unpark"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "UnPark"
  - phoneCallViewId: string with view ID
  - sendCallTo: string with extension number
  - waitForPickup: string with seconds to wait
"""

    def _get_record_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        action = context.get('action', 'StartRecording')
        return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to {action.lower()} for call {context.get('call_id')} on extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-start-stop-recording"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "{action}"
  - phoneCallViewId: string with view ID
  - format: string with recording format (only for StartRecording)
"""

    def _get_transfer_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        action = context.get('action', 'Transfer')
        if action == "Transfer":
            return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to transfer call {context.get('call_id')} from extension {context.get('extension')} to {context.get('destination')}.

Return JSON with:
- tool: must be "phone-calls-update-transfer"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "Transfer"
  - sendCallTo: string with destination number
  - transferFromNumber: string with source number
"""
        else:
            return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to transfer call {context.get('call_id')} to voicemail for extension {context.get('extension')}.

Return JSON with:
- tool: must be "phone-calls-update-transfer-tovoicemail"
- params: an object with:
  - userId: "@me"
  - extension: string with extension number
  - phoneCallId: string with call ID
  - action: "TransferToVoicemail"
  - sendCallTo: string with destination number
  - transferNumber: string with extension number
"""

    def _get_cdr_prompt(self, tools: List[str], context: Dict[str, Any]) -> str:
        start_date = context.get('startDate')
        end_date = context.get('endDate')
        source = context.get('source')
        disposition = context.get('disposition')
        
        return f"""You are an assistant with access to VoIP tools: {', '.join(tools)}.
Your task is to retrieve call history records with the following parameters:
- Start date: {start_date}
- End date: {end_date}
{f'- Source: {source}' if source else ''}
{f'- Disposition: {disposition}' if disposition else ''}

Return JSON with:
- tool: must be "cdr-list"
- params: an object with:
  - startDate: string with query start date in ISO format
  - endDate: string with query end date in ISO format
  - count: string with number of records (default "50")
  - fields: array of field names to return (e.g. ["id", "source", "destination", "disposition", "answered"])
  - ownerId: "@me"
{f'  - source: "@self"' if source else ''}
{f'  - disposition: "{disposition}"' if disposition else ''}

IMPORTANT: Only include source and disposition parameters if they are specified. Do not include them with 'any' or empty values.
"""

    def _get_fallback_parameters(self, test_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get fallback parameters when AI generation fails"""
        context = context or {}
        extension = context.get('extension') or os.getenv("TEST_EXTENSION")
        destination = context.get('destination') or os.getenv("TEST_DESTINATION")
        call_id = context.get('call_id', '')
        view_id = context.get('view_id', '')
        start_date = context.get('startDate')
        end_date = context.get('endDate')

        fallbacks = {
            "create": {
                "tool": "phone-calls-create",
                "params": {
                    "type": "simple",
                    "source": [extension],
                    "destination": [destination],
                    "extension": extension,
                    "userId": "@me"
                }
            },
            "cdr": {
                "tool": "cdr-list",
                "params": {
                    "startDate": start_date,
                    "endDate": end_date,
                    "count": "50",
                    "source": context.get('source'),
                    "disposition": context.get('disposition'),
                    "fields": ["id", "source", "destination", "disposition", "answered"],
                    "ownerId": "@me"
                }
            },
            "hold": {
                "tool": "phone-calls-update-onhold-offhold",
                "params": {
                    "userId": "@me",
                    "extension": extension,
                    "phoneCallId": call_id,
                    "action": context.get('action', 'OnHold'),
                    "phoneCallViewId": view_id
                }
            },
            "monitor": {
                "tool": "phone-calls-update-monitor",
                "params": {
                    "userId": "@me",
                    "extension": extension,
                    "phoneCallId": call_id,
                    "action": "Monitor",
                    "sendCallTo": extension,
                    "phoneCallViewId": view_id
                }
            },
            "park": {
                "tool": "phone-calls-update-park",
                "params": {
                    "userId": "@me",
                    "extension": extension,
                    "phoneCallId": call_id,
                    "action": context.get('action', 'Park'),
                    "phoneCallViewId": view_id,
                    "maxInParking": 180
                }
            },
            "record": {
                "tool": "phone-calls-update-start-stop-recording",
                "params": {
                    "userId": "@me",
                    "extension": extension,
                    "phoneCallId": call_id,
                    "action": context.get('action', 'StartRecording'),
                    "phoneCallViewId": view_id,
                    "format": "wav"
                }
            },
            "transfer": {
                "tool": "phone-calls-update-transfer",
                "params": {
                    "userId": "@me",
                    "extension": extension,
                    "phoneCallId": call_id,
                    "action": context.get('action', 'Transfer'),
                    "sendCallTo": destination,
                    "transferFromNumber": extension
                }
            },
            "cdr": {
                "tool": "cdr-list",
                "params": {
                    "startIndex": "0",
                    "count": "10"
                }
            }
        }

        return fallbacks.get(test_type, fallbacks["create"])
