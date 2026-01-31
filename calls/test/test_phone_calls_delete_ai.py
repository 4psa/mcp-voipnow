import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test call deletion
    call_id = "<CALL_ID_TO_DELETE>"  # Replace with the actual call ID to delete

    if call_id == "<CALL_ID_TO_DELETE>":
        print("No specific call ID provided. Deleting all calls for the extension...")
        if await test.test_delete_all_calls():
            print("All calls for the extension deleted successfully.")
        else:
            print("Failed to delete all calls for the extension.")
    else:
        if await test.test_delete_call(call_id):
            print(f"Call with ID {call_id} deleted successfully")
        else:
            print(f"Failed to delete call with ID {call_id}")

    # Test deleting all calls when no specific call ID is provided
    print("\nTesting deletion of all calls for the extension...")
    if await test.test_delete_all_calls():
        print("All calls for the extension deleted successfully.")
    else:
        print("Failed to delete all calls for the extension.")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
