# filepath: /root/mcp-voipnow-calls/test/test_phone_calls_transfer_ai.py
import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test transfer functionality
    if await test.test_transfer_call():
        print("Transfer test passed")
        # Wait before trying voicemail transfer
        await asyncio.sleep(2)
        if await test.test_transfer_to_voicemail():
            print("Voicemail transfer test passed")
        else:
            print("Voicemail transfer test failed")
    else:
        print("Transfer test failed")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
