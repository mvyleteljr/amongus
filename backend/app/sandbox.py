"""Code sandbox for running submitted code against test cases."""

import subprocess
import json
from typing import Any

from .models import TestResult, FailedTest


def run_tests(code: str, function_name: str, test_cases: list[dict[str, Any]]) -> TestResult:
    """Run code against test cases in isolated subprocess."""
    results = {
        "passed": True,
        "totalTests": len(test_cases),
        "passedTests": 0,
        "failedTests": [],
        "error": None,
    }

    for i, test in enumerate(test_cases):
        args = test["input"]
        expected = test["expected"]

        test_script = f"""
import json
{code}
args = {json.dumps(args)}
result = {function_name}(*args)
print(json.dumps(result))
"""

        try:
            proc = subprocess.run(
                ["python3", "-c", test_script],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if proc.returncode != 0:
                results["passed"] = False
                results["failedTests"].append(
                    FailedTest(
                        testIndex=i,
                        input=args,
                        expected=expected,
                        error=proc.stderr.strip()[-500:],
                    )
                )
            else:
                actual = json.loads(proc.stdout.strip())
                if actual == expected:
                    results["passedTests"] += 1
                else:
                    results["passed"] = False
                    results["failedTests"].append(
                        FailedTest(
                            testIndex=i,
                            input=args,
                            expected=expected,
                            actual=actual,
                        )
                    )

        except subprocess.TimeoutExpired:
            results["passed"] = False
            results["failedTests"].append(
                FailedTest(
                    testIndex=i,
                    input=args,
                    expected=expected,
                    error="TIMEOUT (>5s)",
                )
            )
        except json.JSONDecodeError:
            results["passed"] = False
            results["failedTests"].append(
                FailedTest(
                    testIndex=i,
                    input=args,
                    expected=expected,
                    error=f"Invalid output: {proc.stdout.strip()[:200]}",
                )
            )
        except Exception as e:
            results["passed"] = False
            results["failedTests"].append(
                FailedTest(
                    testIndex=i,
                    input=args,
                    expected=expected,
                    error=str(e),
                )
            )

    return TestResult(**results)
