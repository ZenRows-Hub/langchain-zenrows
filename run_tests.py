#!/usr/bin/env python3
"""Test runner script for langchain-zenrows package."""

import os
import sys
import subprocess
import argparse


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print("Make sure pytest is installed: pip install pytest")
        return False


def check_api_key():
    """Check if ZenRows API key is set."""
    api_key = os.environ.get("ZENROWS_API_KEY")
    if api_key:
        print(f"✅ ZENROWS_API_KEY is set (starts with: {api_key[:10]}...)")
        return True
    else:
        print("⚠️  ZENROWS_API_KEY is not set")
        print("   Integration tests will be skipped")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run tests for langchain-zenrows")
    parser.add_argument(
        "--unit-only", action="store_true", help="Run only unit tests (no API calls)"
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Run only integration tests (requires API key)",
    )
    parser.add_argument("--no-slow", action="store_true", help="Skip slow tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("🧪 LangChain-ZenRows Test Runner")
    print("=" * 50)

    # Check environment
    has_api_key = check_api_key()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.coverage:
        cmd.extend(
            [
                "--cov=langchain_zenrows",
                "--cov-report=html",
                "--cov-report=term-missing",
            ]
        )

    # Test selection
    if args.unit_only:
        cmd.append("tests/unit_tests/")
        print("🔧 Running unit tests only")
    elif args.integration_only:
        if not has_api_key:
            print("❌ Cannot run integration tests without ZENROWS_API_KEY")
            return 1
        cmd.extend(["-m", "integration", "tests/integration_tests/"])
        print("🌐 Running integration tests only")
    else:
        cmd.append("tests/")
        print("🔄 Running all tests")

    # Skip slow tests if requested
    if args.no_slow:
        cmd.extend(["-m", "not slow"])
        print("⚡ Skipping slow tests")

    # Show what will be run
    print(f"\nTest command: {' '.join(cmd)}")

    if not has_api_key and not args.unit_only:
        print("\n⚠️  Note: Integration tests will be skipped due to missing API key")
        print("   Set ZENROWS_API_KEY environment variable to run integration tests")

    # Run tests
    success = run_command(cmd, "Test execution")

    if success:
        print("\n🎉 All tests completed successfully!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
