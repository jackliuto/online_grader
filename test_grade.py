import os
from pathlib import Path
import requests

# Default URL for server_test.py app
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")
PROBLEM_NAME = os.getenv("PROBLEM_NAME", "p01.pddl")


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main() -> None:
    # Adjust filenames here if yours differ
    domain_path = "domain.pddl"
    problem_path = "p01.pddl"
    plan_path = "plan.p01.pddl"

    domain = read_text(domain_path)
    problem = read_text(problem_path)
    plan = read_text(plan_path)

    # JSON POST to /grade
    payload = {
        "domain": domain,
        "problem": problem,
        "plan": plan,
        "meta": {"problem_name": PROBLEM_NAME, "source": "json"},
    }
    try:
        r = requests.post(f"{SERVER_URL}/grade", json=payload, timeout=120)
        print("POST /grade ->", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print("Error calling /grade:", e)

    # Multipart upload to /grade-file
    files = {
        "domain": ("domain.pddl", domain, "text/plain"),
        "problem": (PROBLEM_NAME, problem, "text/plain"),
        "plan": (f"plan.{PROBLEM_NAME}", plan, "text/plain"),
    }
    try:
        r2 = requests.post(f"{SERVER_URL}/grade-file", files=files, timeout=120)
        print("POST /grade-file ->", r2.status_code)
        try:
            print(r2.json())
        except Exception:
            print(r2.text)
    except Exception as e:
        print("Error calling /grade-file:", e)


if __name__ == "__main__":
    main()
