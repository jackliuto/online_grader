import os
from pathlib import Path
import requests

# Default URL for server_test.py app
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main() -> None:
    # Adjust filenames here if yours differ
    domain_path = "data/submission/domain.pddl"
    problem_path = "data/submission/p01.pddl"
    # plan_path = "data/submission/plan.p01.pddl"
    problem_id = "1" # <--- Change this to test p01, p02, or p03

    domain = read_text(domain_path)
    problem = read_text(problem_path)
    # plan = read_text(plan_path)

    # JSON POST to /grade
    payload = {
        "domain": domain,
        "problem": problem,
        # "plan": plan,
        "problem_id": problem_id
    }
    try:
        r = requests.post(f"{SERVER_URL}/grade-file", json=payload, timeout=60)
        print("POST /grade-file ->", r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)
    except Exception as e:
        print("Error calling /grade:", e)

    # # Multipart upload to /grade-file
    # files = {
    #     "domain": ("domain.pddl", domain, "text/plain"),
    #     "plan": ("plan.pddl", plan, "text/plain"),
    # }
    # data = {"problem_id": problem_id}
    # try:
    #     r2 = requests.post(f"{SERVER_URL}/grade-file", files=files, data=data, timeout=120)
    #     print("POST /grade-file ->", r2.status_code)
    #     try:
    #         print(r2.json())
    #     except Exception:
    #         print(r2.text)
    # except Exception as e:
    #     print("Error calling /grade-file:", e)


if __name__ == "__main__":
    main()
