import asyncio
from test_class import VoIPTestSuite

async def main() -> None:
    test = VoIPTestSuite()
    if not await test.setup():
        print("Test setup failed")
        return

    # Run each test case
    tests = [
        ("Recent calls test", test.test_list_recent_calls),
        ("Extension calls test", test.test_list_by_extension),
        ("Disposition calls test", test.test_list_by_disposition)
    ]
    
    failed_tests = 0
    for name, test_func in tests:
        print(f"\nRunning {name}...")
        if await test_func():
            print(f"{name} passed")
        else:
            print(f"{name} failed")
            failed_tests += 1
    
    if failed_tests > 0:
        print(f"\n{failed_tests} test(s) failed!")
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    asyncio.run(main())
