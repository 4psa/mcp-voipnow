import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Test monitor functionality
    monitoring_extension = "0003*003"  # Example monitoring extension
    if await test.test_monitor_call(monitoring_extension):
        print("Monitor test passed")
    else:
        print("Monitor test failed")

    await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
