import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test hold functionality
    if await test.test_hold_call():
        print("Hold test passed")
        if await test.test_unhold_call():
            print("Unhold test passed")
        else:
            print("Unhold test failed")
    else:
        print("Hold test failed")

    # Ensure cleanup is always called
    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
