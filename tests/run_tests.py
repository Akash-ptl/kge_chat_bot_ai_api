#!/usr/bin/env python3
"""
Simple test runner to demonstrate the multi-tenant functionality.
This script will start the API server and run the multi-tenant tests.
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_api_server():
    """Start the FastAPI server in the background."""
    print("🚀 Starting API server...")

    # Change to the app directory
    app_dir = Path(__file__).parent.parent / "app"

    # Start the server using uvicorn
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=app_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait a bit for the server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)

    return process

def run_tests():
    """Run the multi-tenant tests."""
    print("🧪 Running multi-tenant tests...")

    # Run the multi-tenant test
    test_file = Path(__file__).parent / "test_multi_tenant.py"
    result = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True)

    print("Test Output:")
    print(result.stdout)
    if result.stderr:
        print("Test Errors:")
        print(result.stderr)

    return result.returncode == 0

def main():
    """Main test runner function."""
    print("=" * 60)
    print("🎯 Multi-Tenant AI Chat Bot Test Runner")
    print("=" * 60)

    # Check if environment is set up
    if not os.getenv("MONGO_URL"):
        print("❌ Please set MONGO_URL environment variable")
        return 1

    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set - using test value")

    server_process = None
    try:
        # Start the API server
        server_process = start_api_server()

        # Run tests
        test_success = run_tests()

        if test_success:
            print("\n✅ All tests completed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Test runner interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1
    finally:
        # Clean up the server process
        if server_process:
            print("\n🛑 Stopping API server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()

if __name__ == "__main__":
    sys.exit(main())
