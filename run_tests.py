#!/usr/bin/env python3
"""
Test runner for BTC Tennis Bot
Runs all unit tests with coverage reporting
"""
import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running BTC Tennis Bot Test Suite")
    print("=" * 50)

    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "--cov=core",
        "--cov=btc_tennis_bot",
        "--cov=daemon_monitoring",
        "--cov=run_background_env",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml",
        "--cov-fail-under=100",
        "-v",
    ]

    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed with 100% coverage!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
