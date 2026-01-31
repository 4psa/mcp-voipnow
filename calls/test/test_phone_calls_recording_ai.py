import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test recording functionality
    if await test.test_start_recording():
        print("Start recording test passed")
        # Wait a few seconds for recording
        await asyncio.sleep(5)
        if await test.test_stop_recording():
            print("Stop recording test passed")
        else:
            print("Stop recording test failed")
    else:
        print("Start recording test failed")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())