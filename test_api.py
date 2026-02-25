#!/usr/bin/env python
"""
Test script for Sales Analytics Chatbot.
Run: python test_api.py
"""

import json
import time
from typing import Any

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    exit(1)

BASE_URL = "http://localhost:8000"

# Test queries
TEST_QUERIES = [
    "What were total sales last month?",
    "Which region had highest revenue?",
    "Show top 5 products by revenue",
    "Compare Q3 vs Q4 sales",
    "Sales by category",
    "How many transactions in East region?",
    "What is average transaction value?",
]


class APITester:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.results = []

    def test_health(self) -> bool:
        print("[1] Testing /health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Status: {data['status']}")
                print(f"  ✓ Service: {data['service']}")
                print(f"  ✓ Environment: {data['environment']}")
                return True
            else:
                print(f"  ✗ HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Connection failed: {e}")
            print(f"    Ensure backend is running: uvicorn app.main:app --reload")
            return False

    def test_chat(self, question: str) -> dict[str, Any] | None:
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"question": question},
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ✗ HTTP {response.status_code}")
                print(f"    {response.text}")
                return None
        except requests.exceptions.Timeout:
            print(f"  ✗ Request timeout (30s).")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {e}")
            return None

    def print_result(self, question: str, result: dict[str, Any]) -> None:
        print(f"\n  Q: {question}")
        print(f"  A: {result['answer']}")
        print(f"  SQL: {result['generated_sql'][:100]}...")
        if result['data_preview']:
            print(f"  Rows: {len(result['data_preview'])}")
            print(f"  Sample: {json.dumps(result['data_preview'][0], indent=2)[:200]}...")

    def run_all_tests(self) -> None:
        print("=" * 60)
        print("Sales Analytics Chatbot - API Test Suite")
        print("=" * 60)

        # Test health
        if not self.test_health():
            return

        # Test chat queries
        print("\n[2] Testing /chat endpoint...")
        for i, query in enumerate(TEST_QUERIES[:3], 1):
            print(f"\n  [{i}] Query: '{query}'")
            result = self.test_chat(query)
            if result:
                self.print_result(query, result)
                self.results.append((query, "PASS"))
            else:
                self.results.append((query, "FAIL"))
            time.sleep(1)

        # Test invalid input
        print("\n[3] Testing error handling...")
        print("  Testing empty question...")
        result = self.test_chat("")
        if result is None:
            print("  ✓ Empty question properly rejected")
            self.results.append(("empty_question", "PASS"))
        else:
            print("  ✗ Empty question should fail")
            self.results.append(("empty_question", "FAIL"))

        # Summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        passed = sum(1 for _, status in self.results if status == "PASS")
        total = len(self.results)
        print(f"Passed: {passed}/{total}")

        if passed == total:
            print("✓ All tests passed!")
        else:
            print("✗ Some tests failed. Check logs above.")

        for query, status in self.results:
            symbol = "✓" if status == "PASS" else "✗"
            print(f"  {symbol} {query[:40]:<40} {status}")


if __name__ == "__main__":
    tester = APITester(BASE_URL)
    tester.run_all_tests()
