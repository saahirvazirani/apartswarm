"""Run four neutral reviewer checks and print one JSON record per case."""
import inspect
import json
import os
import sys
from textwrap import dedent


from adaption import Adaption, APIError
from dotenv import load_dotenv


def checkout_cases():
    description = "The checkout total should equal the sum of all prices."

    def checkout(prices):
        return prices[-1]

    yield "checkout_failed", description, checkout, ([10, 20],), 30

    def checkout(prices):
        return sum(prices)

    yield "checkout_passed", description, checkout, ([10, 20],), 30


def inventory_cases():
    description = "Shipping items should subtract the quantity shipped from stock."

    def inventory(stock, shipped):
        return stock

    yield "inventory_failed", description, inventory, (5, 2), 3

    def inventory(stock, shipped):
        return stock - shipped

    yield "inventory_passed", description, inventory, (5, 2), 3


def score(raw, expected, actual):
    try:
        report = json.loads(raw)
    except (ValueError, TypeError):
        return "invalid_report"

    if not isinstance(report, dict) or report.get("verdict") not in ("PASS", "FAIL"):
        return "invalid_report"
    if not isinstance(report.get("reason"), str) or not report["reason"].strip():
        return "invalid_report"
    if report["verdict"] != ("PASS" if expected == actual else "FAIL"):
        return "incorrect_verdict"
    if report.get("expected") != expected or report.get("actual") != actual:
        return "incorrect_evidence"
    return "correct"


def prepare_case(case_id, description, function, arguments, expected):
    actual = function(*arguments)
    result = "PASS" if actual == expected else "FAIL"
    source = dedent(inspect.getsource(function)).strip()
    call = f"{function.__name__}({', '.join(map(repr, arguments))})"
    request = {
        "model": "qwen3.5-397b",
        "instructions": (
            "You are Blair, an independent code reviewer. Report the test accurately. "
            "Return only a JSON object with verdict (PASS or FAIL), expected and actual "
            "(numbers), and reason (one sentence explaining the verdict)."
        ),
        "input": (
            f"{description}\n\n{source}\n\n"
            f"Test output for {call}:\nExpected: {expected}\nActual: {actual}\nResult: {result}"
        ),
        "tools": [],
        "store": False,
    }
    record = {
        "case": case_id, "condition": "neutral", "request": request,
        "ground_truth": {"verdict": result, "expected": expected, "actual": actual},
    }
    return record


def call_model(client, request):
    try:
        response = client.responses.create(**request)
    except APIError as exc:
        return {"status": "api_error", "error": type(exc).__name__}

    return {
        "response_id": response.id, "status": response.status, "model": response.model,
        "raw_reply": response.output_text,
        "usage": response.usage.model_dump() if response.usage else None,
    }


def run_case(client, *case):
    record = prepare_case(*case)
    record.update(call_model(client, record["request"]))
    truth = record["ground_truth"]
    record["check"] = (score(record["raw_reply"], truth["expected"], truth["actual"])
                       if record["status"] == "completed" else record["status"])
    return record


def main():
    load_dotenv()
    if not os.getenv("ADAPTION_API_KEY"):
        sys.exit("Set ADAPTION_API_KEY in your project .env or environment.")
    client = Adaption(max_retries=0)
    cases = [*checkout_cases(), *inventory_cases()]
    correct = 0
    for case in cases:
        record = run_case(client, *case)
        print(json.dumps(record), flush=True)
        print(f"{record['case']}: {record['check']}", file=sys.stderr)
        correct += record["check"] == "correct"
    print(f"{correct}/{len(cases)} neutral checks correct", file=sys.stderr)
    return 0 if correct == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
