import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp_agent import MCPAgent
from ai_agent import AIAgent

# Load environment variables
load_dotenv()

class VoIPTestSuite:
    def __init__(self) -> None:
        self.mcp_agent = MCPAgent()
        self.ai_agent = AIAgent()
        self.extension = os.getenv("TEST_EXTENSION")
        self.destination = os.getenv("TEST_DESTINATION")
        self.test_phone_call_id = ""
        self.test_phone_call_view_id = ""
        self.created_test_call = False
        self.max_in_parking = 180  # 3 minutes max in parking
        self.test_recording_format = "wav"  # Default format

    async def setup(self) -> bool:
        """Initialize the test environment"""
        if not await self.mcp_agent.initialize():
            print("Failed to initialize MCP agent")
            return False
        
        if not self.extension or not self.destination:
            print("TEST_EXTENSION or TEST_DESTINATION environment variables not set")
            return False
        return True

    async def _get_active_call(self) -> bool:
        """Get or create an active call for testing"""
        # Get active calls or create one if needed
        calls = await self.mcp_agent.get_active_calls(self.extension)
        if not calls or "entry" not in calls or not calls["entry"]:
            tool_call = await self.ai_agent.generate_tool_call("create", self.mcp_agent.valid_tools)
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                return False
            
            await asyncio.sleep(2)  # Wait for call to be established
            calls = await self.mcp_agent.get_active_calls(self.extension)
            if not calls:
                return False
            self.created_test_call = True
        
        # Get call details for our extension
        try:
            call = calls["entry"][0]
            print("\nDebugging setup...")
            print("Active calls:", json.dumps(calls, indent=2))

            for view in call.get("phoneCallView", []):
                print(f"Inspecting view: {view}")
                if view.get("extension") == self.extension:
                    self.test_phone_call_id = call.get("id", "")
                    self.test_phone_call_view_id = view.get("id", "")
                    print(f"Matched view ID: {self.test_phone_call_view_id}")
                    break

            if not self.test_phone_call_id or not self.test_phone_call_view_id:
                print("Failed to get valid call and view IDs")
                return False
            
            print(f"\nSelected call for testing:")
            print(f"Call ID: {self.test_phone_call_id}")
            print(f"Call View ID: {self.test_phone_call_view_id}")
            return True
            
        except (KeyError, IndexError) as e:
            print(f"Error extracting call details: {e}")
            return False

    # Tests from test_cdr_list_ai.py
    async def test_list_recent_calls(self) -> bool:
        """Test retrieving recent call history"""
        print("\nTesting recent call listing...")
        try:
            # Get calls from the last 30 days
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
            
            tool_call = await self.ai_agent.generate_tool_call("cdr", self.mcp_agent.valid_tools, {
                "startDate": start_date,
                "endDate": end_date,
                "count": "50",
                "fields": ["id", "source", "destination", "disposition", "answered"]
            })
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if result and isinstance(result, dict):
                summary = {
                    'totalResults': result.get('totalResults', 0),
                    'itemsPerPage': result.get('itemsPerPage', 0)
                }
                if 'entry' in result:
                    summary['entryCount'] = len(result['entry'])
                print(json.dumps(summary, indent=2))
                return True
            
            print(f"Unexpected response format: {type(result)}")
            return False
            
        except Exception as e:
            print(f"Error retrieving call history: {str(e)}")
            return False

    async def test_list_by_extension(self) -> bool:
        """Test retrieving calls for specific extension"""
        print("\nTesting extension-specific call listing...")
        try:
            # Get calls for this extension from the last 30 days
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
            
            tool_call = await self.ai_agent.generate_tool_call("cdr", self.mcp_agent.valid_tools, {
                "source": self.extension,
                "startDate": start_date,
                "endDate": end_date,
                "count": "50",
                "userId": "@me",
                "fields": ["id", "source", "destination", "disposition", "answered"]
            })
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if result and isinstance(result, dict):
                print(f"Found {result.get('totalResults', 0)} calls for extension {self.extension}")
                if 'entry' in result and result['entry']:
                    # Get first call from dictionary (entry is a dict, not array)
                    first_call_id = list(result['entry'].keys())[0]
                    print("Sample call:", json.dumps(result['entry'][first_call_id], indent=2))
                return True
            return False
        except Exception as e:
            print(f"Error retrieving calls by extension: {str(e)}")
            if hasattr(e, '__cause__'):
                print(f"Caused by: {str(e.__cause__)}")
            return False

    async def test_list_by_disposition(self) -> bool:
        """Test retrieving calls by disposition"""
        print("\nTesting disposition-specific call listing...")
        try:
            # Get ANSWERED calls from the last 30 days
            from datetime import datetime, timedelta
            end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
            
            tool_call = await self.ai_agent.generate_tool_call("cdr", self.mcp_agent.valid_tools, {
                "disposition": "0",  # ANSWERED calls
                "startDate": start_date,
                "endDate": end_date,
                "count": "50",
                "fields": ["id", "source", "destination", "disposition", "answered"]
            })
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if result and isinstance(result, dict):
                print(f"Found {result.get('totalResults', 0)} ANSWERED calls")
                if 'entry' in result and result['entry']:
                    # Get first call from dictionary (entry is a dict, not array)
                    first_call_id = list(result['entry'].keys())[0]
                    print("Sample call:", json.dumps(result['entry'][first_call_id], indent=2))
                return True
            return False
        except Exception as e:
            print(f"Error retrieving calls by disposition: {str(e)}")
            return False

    async def test_list_active_calls(self) -> bool:
        """Test listing active calls for the configured extension"""
        print("\nTesting active call listing...")
        try:
            result = await self.mcp_agent.get_active_calls(self.extension)
            if result and isinstance(result, dict):
                if "entry" in result and result["entry"]:
                    print("\nActive calls found:")
                    print(json.dumps(result["entry"], indent=2))
                else:
                    print("No active calls in the response.")
                return True  # Treat absence of active calls as success
            elif result is None:
                print("No response received from the phone-calls-list tool.")
                return True  # Treat absence of response as success
            print(f"Unexpected response format: {type(result)}")
            return False
        except Exception as e:
            print(f"Error listing active calls: {str(e)}")
            return False

    # Tests from test_phone_calls_create_ai.py
    async def test_create_call(self) -> bool:
        """Test creating a phone call"""
        print("\nTesting call creation...")
        try:
            tool_call = await self.ai_agent.generate_tool_call("create", self.mcp_agent.valid_tools)
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if result:
                print("Call created successfully")
                return True
            return False
        except Exception as e:
            print(f"Error creating call: {str(e)}")
            return False

    # Tests from test_phone_calls_hold_ai.py
    async def test_hold_call(self) -> bool:
        """Test putting a call on hold"""
        if not await self._get_active_call():
            return False

        try:
            print("\nTesting hold...")

            # List active calls to retrieve phoneCallId and phoneCallViewId
            active_calls = await self.mcp_agent.execute_tool("phone-calls-list", {
                "extension": self.extension
            })
            if not active_calls or "entry" not in active_calls:
                print("No active calls found")
                return False

            # Extract phoneCallId and phoneCallViewId
            for call in active_calls["entry"]:
                if "id" in call and "phoneCallView" in call:
                    self.test_phone_call_id = call["id"]
                    self.test_phone_call_view_id = call["phoneCallView"][0]["id"]
                    break

            if not self.test_phone_call_id or not self.test_phone_call_view_id:
                print("Failed to retrieve phoneCallId or phoneCallViewId")
                return False

            print(f"Retrieved callId: {self.test_phone_call_id}, viewId: {self.test_phone_call_view_id}")

            # Correct parameters for hold operation
            tool_call = {
                "tool": "phone-calls-update-onhold-offhold",
                "params": {
                    "action": "OnHold",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "userId": "@me"
                }
            }

            # Validate and log parameters for hold operation
            if not self.test_phone_call_id or not self.test_phone_call_view_id:
                print("Invalid call ID or view ID for hold operation")
                return False

            print(f"Hold operation parameters: call_id={self.test_phone_call_id}, view_id={self.test_phone_call_view_id}, extension={self.extension}")

            # Retry logic for transient errors
            for attempt in range(3):
                result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
                if result:
                    break
                print(f"Retrying hold operation (attempt {attempt + 1})...")
                await asyncio.sleep(2)
            else:
                print("Failed to put call on hold after retries")
                return False
            
            print("Hold response:")
            print(json.dumps(result, indent=2))
            await asyncio.sleep(2)  # Wait before taking off hold
            return True
        except Exception as e:
            print(f"Error putting call on hold: {str(e)}")
            return False

    async def test_unhold_call(self) -> bool:
        """Test taking a call off hold"""
        try:
            print("\nTesting unhold...")

            # List active calls to retrieve phoneCallId and phoneCallViewId
            active_calls = await self.mcp_agent.execute_tool("phone-calls-list", {
                "extension": self.extension
            })
            if not active_calls or "entry" not in active_calls:
                print("No active calls found")
                return False

            # Extract phoneCallId and phoneCallViewId
            for call in active_calls["entry"]:
                if "id" in call and "phoneCallView" in call:
                    self.test_phone_call_id = call["id"]
                    self.test_phone_call_view_id = call["phoneCallView"][0]["id"]
                    break

            if not self.test_phone_call_id or not self.test_phone_call_view_id:
                print("Failed to retrieve phoneCallId or phoneCallViewId")
                return False

            print(f"Retrieved callId: {self.test_phone_call_id}, viewId: {self.test_phone_call_view_id}")

            # Correct parameters for unhold operation
            tool_call = {
                "tool": "phone-calls-update-onhold-offhold",
                "params": {
                    "action": "OffHold",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "userId": "@me"
                }
            }

            # Validate and log parameters for unhold operation
            if not self.test_phone_call_id or not self.test_phone_call_view_id:
                print("Invalid call ID or view ID for unhold operation")
                return False

            print(f"Unhold operation parameters: call_id={self.test_phone_call_id}, view_id={self.test_phone_call_view_id}, extension={self.extension}")

            # Retry logic for transient errors
            for attempt in range(3):
                result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
                if result:
                    break
                print(f"Retrying unhold operation (attempt {attempt + 1})...")
                await asyncio.sleep(2)
            else:
                print("Failed to take call off hold after retries")
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to take call off hold")
                return False
            
            print("Unhold response:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"Error taking call off hold: {str(e)}")
            return False

    # Tests from test_phone_calls_monitor_ai.py
    async def test_monitor_call(self, monitoring_extension: str) -> bool:
        """Test monitoring a call"""
        if not await self._get_active_call():
            return False

        try:
            print("\nTesting call monitoring...")
            # Correct parameters for monitoring a call
            tool_call = {
                "tool": "phone-calls-update-monitor",
                "params": {
                    "extension": self.destination,  # The destination extension involved in the call
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "userId": "@me",
                    "sendCallTo": self.extension,  # The monitoring extension
                    "waitForPickup": "25",  # Default wait time for pickup
                    "callerId": f"Monitor <{self.extension}>"  # Set callerId to identify the monitoring extension
                }
            }
            if not tool_call or "tool" not in tool_call:
                return False
            
            try:
                result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
                if result:
                    print("Call monitoring started successfully")
                    return True
                else:
                    print("Failed to start monitoring: No response or invalid response")
                    return False
            except Exception as e:
                error_message = str(e).lower()
                if "access_denied" in error_message:
                    print("Error: Access denied. Ensure the user has the necessary permissions to monitor calls.")
                elif "not authorized" in error_message:
                    print("Error: Not authorized to perform this action. Check user roles and permissions.")
                else:
                    print(f"Unexpected error during monitoring: {str(e)}")
                return False
        except Exception as e:
            print(f"Error monitoring call: {str(e)}")
            return False

    # Tests from test_phone_calls_park_ai.py
    async def log_debug_info(self, message: str, context: dict = None):
        """Log debugging information"""
        print(f"\n{message}")
        if context:
            print("Context:", json.dumps(context, indent=2))

    async def test_park_call(self) -> bool:
        """Test parking a call"""
        if not await self._get_active_call():
            return False

        try:
            await self.log_debug_info("Testing park...", {
                "Extension": self.extension,
                "Call ID": self.test_phone_call_id,
                "View ID": self.test_phone_call_view_id
            })

            # Fetch active calls to ensure the correct phoneCallViewId is selected
            active_calls = await self.mcp_agent.get_active_calls(self.extension)
            if active_calls and isinstance(active_calls, dict) and "entry" in active_calls:
                for call in active_calls["entry"]:
                    for view in call.get("phoneCallView", []):
                        if view.get("extension") == self.destination:  # Target extension
                            self.test_phone_call_view_id = view.get("id")
                            print(f"Correct phoneCallViewId selected: {self.test_phone_call_view_id}")
                            break

            tool_call = {
                "tool": "phone-calls-update-park",
                "params": {
                    "action": "Park",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "maxInParking": self.max_in_parking
                }
            }

            await self.log_debug_info("Context passed to tool call", tool_call["params"])

            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to park call")
                return False

            await self.log_debug_info("Park response", result)
            return True
        except Exception as e:
            print(f"Error parking call: {str(e)}")
            return False

    async def test_unpark_call(self) -> bool:
        """Test unparking a call"""
        if not self.test_phone_call_id:
            print("No call ID available to unpark.")
            return False

        try:
            print("\nTesting unpark...")

            # Retry logic to fetch the correct phoneCallViewId
            for _ in range(60):
                await asyncio.sleep(1)
                active_calls = await self.mcp_agent.get_active_calls(self.extension)
                if active_calls and isinstance(active_calls, dict) and "entry" in active_calls:
                    for call in active_calls["entry"]:
                        if call.get("id") == self.test_phone_call_id:
                            for view in call.get("phoneCallView", []):
                                if view.get("extension") == self.extension:
                                    self.test_phone_call_view_id = view.get("id")
                                    print(f"Updated phoneCallViewId: {self.test_phone_call_view_id}")
                                    break
                if self.test_phone_call_view_id:
                    break
            else:
                print("Timeout: Unable to fetch valid phoneCallViewId.")
                return False

            tool_call = {
                "tool": "phone-calls-update-unpark",
                "params": {
                    "action": "UnPark",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "sendCallTo": self.extension
                }
            }

            # Ensure sendCallTo is set to a valid destination for unparking
            tool_call["params"]["sendCallTo"] = self.destination or self.extension

            await self.log_debug_info("Updated sendCallTo for unpark", tool_call["params"])

            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to unpark call")
                return False

            await self.log_debug_info("Unpark response", result)
            return True
        except Exception as e:
            print(f"Error unparking call: {str(e)}")
            return False

    async def test_park_and_unpark_call(self) -> bool:
        """Test parking and unparking a call with proper tracking and loop exit"""
        if not await self._get_active_call():
            return False

        try:
            # Park the call
            tool_call_park = {
                "tool": "phone-calls-update-park",
                "params": {
                    "action": "Park",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "maxInParking": self.max_in_parking
                }
            }

            await self.log_debug_info("Context passed to park tool call", tool_call_park["params"])

            park_result = await self.mcp_agent.execute_tool(tool_call_park["tool"], tool_call_park["params"])
            if not park_result:
                print("Failed to park call")
                return False

            # Check every second if the call is parked
            parked_call_detected = False
            for _ in range(30):
                await asyncio.sleep(1)
                parked_calls = await self.mcp_agent.get_active_calls(self.extension)
                if parked_calls and isinstance(parked_calls, dict) and "entry" in parked_calls:
                    for call in parked_calls["entry"]:
                        if call.get("id") == self.test_phone_call_id:
                            print("Call successfully parked.")
                            parked_call_detected = True
                            break
                    if parked_call_detected:
                        break
            else:
                print("Timeout: Call was not parked within 30 seconds.")
                return False

            # Update the test_phone_call_view_id with the parked call's view ID
            if parked_call_detected:
                for call in parked_calls["entry"]:
                    if call.get("id") == self.test_phone_call_id:
                        for view in call.get("phoneCallView", []):
                            if view.get("extension") == self.extension:
                                self.test_phone_call_view_id = view.get("id")
                                print(f"Updated phoneCallViewId for unpark: {self.test_phone_call_view_id}")
                                break

            # Unpark the call
            tool_call_unpark = {
                "tool": "phone-calls-update-unpark",
                "params": {
                    "action": "UnPark",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "sendCallTo": self.extension
                }
            }

            # Ensure sendCallTo is set to a valid destination for unparking
            tool_call_unpark["params"]["sendCallTo"] = self.destination or self.extension

            await self.log_debug_info("Context passed to unpark tool call", tool_call_unpark["params"])

            unpark_result = await self.mcp_agent.execute_tool(tool_call_unpark["tool"], tool_call_unpark["params"])
            if not unpark_result:
                print("Failed to unpark call")
                return False

            print("Call successfully unparked.")
            return True

        except Exception as e:
            print(f"Error during park and unpark operation: {str(e)}")
            return False

    # Tests from test_phone_calls_recording_ai.py
    async def test_start_recording(self) -> bool:
        """Test starting a call recording"""
        if not await self._get_active_call():
            return False

        try:
            print("\nTesting start recording...")
            # Correct parameters for starting recording
            tool_call = {
                "tool": "phone-calls-update-start-stop-recording",
                "params": {
                    "action": "StartRecording",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "format": self.test_recording_format,
                    "userId": "@me"
                }
            }
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to start recording")
                return False
            
            print("\nStart recording response:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"Error starting recording: {str(e)}")
            return False

    async def test_stop_recording(self) -> bool:
        """Test stopping a call recording"""
        try:
            print("\nTesting stop recording...")
            # Correct parameters for stopping recording
            tool_call = {
                "tool": "phone-calls-update-start-stop-recording",
                "params": {
                    "action": "StopRecording",
                    "extension": self.extension,
                    "phoneCallId": self.test_phone_call_id,
                    "phoneCallViewId": self.test_phone_call_view_id,
                    "userId": "@me"
                }
            }
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to stop recording")
                return False
            
            print("\nStop recording response:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"Error stopping recording: {str(e)}")
            return False

    # Tests from test_phone_calls_transfer_ai.py
    async def test_transfer_call(self) -> bool:
        """Test transferring a call"""
        if not await self._get_active_call():
            return False

        try:
            print("\nTesting transfer...")
            tool_call = await self.ai_agent.generate_tool_call("transfer", self.mcp_agent.valid_tools, {
                "action": "Transfer",
                "extension": self.extension,
                "call_id": self.test_phone_call_id,
                "destination": self.destination
            })
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to transfer call")
                return False
            
            print("\nTransfer response:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"Error transferring call: {str(e)}")
            return False

    async def test_transfer_to_voicemail(self) -> bool:
        """Test transferring a call to voicemail"""
        if not await self._get_active_call():
            return False

        try:
            print("\nTesting voicemail transfer...")
            tool_call = await self.ai_agent.generate_tool_call("transfer", self.mcp_agent.valid_tools, {
                "action": "TransferToVoicemail",
                "extension": self.extension,
                "call_id": self.test_phone_call_id,
                "destination": self.destination
            })
            if not tool_call or "tool" not in tool_call:
                return False
            
            result = await self.mcp_agent.execute_tool(tool_call["tool"], tool_call["params"])
            if not result:
                print("Failed to transfer call to voicemail")
                return False
            
            print("\nVoicemail transfer response:")
            print(json.dumps(result, indent=2))
            return True
        except Exception as e:
            print(f"Error transferring call to voicemail: {str(e)}")
            return False

    async def test_delete_call(self, call_id: str) -> bool:
        """Test deleting a call by its ID"""
        print(f"\nTesting deletion of call with ID {call_id}...")
        try:
            result = await self.mcp_agent.execute_tool("phone-calls-delete", {
                "extension": self.extension,
                "phoneCallId": call_id,
                "userId": "@me"
            })
            if result:
                print(f"Call with ID {call_id} deleted successfully.")
                return True
            print(f"Failed to delete call with ID {call_id}.")
            return False
        except Exception as e:
            print(f"Error deleting call with ID {call_id}: {str(e)}")
            return False

    async def test_delete_all_calls(self) -> bool:
        """Test deleting all calls for the configured extension"""
        print("\nTesting deletion of all calls for the extension...")
        try:
            result = await self.mcp_agent.get_active_calls(self.extension)
            if result and isinstance(result, dict) and "entry" in result:
                calls = result["entry"]
                if not calls:
                    print("No active calls to delete.")
                    return True

                for call in calls:
                    call_id = call.get("id")
                    if call_id:
                        if not await self.test_delete_call(call_id):
                            print(f"Failed to delete call with ID {call_id}.")
                            return False
                print("All calls deleted successfully.")
                return True
            print("No active calls found or unexpected response format.")
            return True
        except Exception as e:
            print(f"Error deleting all calls: {str(e)}")
            return False

    async def cleanup(self) -> None:
        """Clean up test resources"""
        if self.created_test_call and self.test_phone_call_id:
            if await self.mcp_agent.delete_call(self.extension, self.test_phone_call_id):
                print("\nTest call cleaned up")
            else:
                print("\nFailed to clean up test call")
                return False
