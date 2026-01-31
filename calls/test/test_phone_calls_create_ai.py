import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test call creation
    if await test.test_create_call():
        print("Call creation test passed")
    else:
        print("Call creation test failed")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

