import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test park functionality
    if await test.test_park_call():
        print("Park test passed")
        # Wait until the call is parked or at most 30 seconds
        for _ in range(30):
            await asyncio.sleep(1)
            parked_calls = await test.mcp_agent.get_active_calls(test.extension)
            if not parked_calls:
                print("Call successfully parked.")
                break
        else:
            print("Timeout: Call was not parked within 30 seconds.")

        # Attempt to unpark the call
        if await test.test_unpark_call():
            print("Unpark test passed")
        else:
            print("Unpark test failed")
    else:
        print("Park test failed")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
