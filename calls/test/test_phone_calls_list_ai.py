import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test active call listing
    if await test.test_list_active_calls():
        print("Active calls listed successfully")
    else:
        print("Failed to list active calls")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
