# server.py
from __future__ import annotations
import os
import tempfile
import shutil
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from grade import Grader

# --- Optional CORS (enable if frontend is separate) ---
ENABLE_CORS = True
try:
    from flask_cors import CORS
except Exception:
    ENABLE_CORS = False

# -----------------------
# App factory
# -----------------------
def create_app() -> Flask:
    app = Flask(__name__)
    if ENABLE_CORS:
        try:
            CORS(app)
        except Exception:
            pass

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "pddl_online_grader"})

    @app.post("/grade")
    def grade():
        """
        JSON input shape:
        {
          "domain": "<PDDL domain text>",      # optional if your grader has a default
          "problem": "<PDDL problem text>",    # optional
          "plan": "<student plan text>",       # required
          "meta": {...}                        # optional, e.g., student id, assignment id
        }
        """
        # 1) Parse & validate inputs
        try:
            payload = request.get_json(force=True, silent=False)
        except Exception:
            return _bad_request("Body must be valid JSON with plan/domain/problem strings.")

        plan = _expect_str(payload, "plan", required=True)
        domain = _expect_str(payload, "domain", required=False)
        problem = _expect_str(payload, "problem", required=False)
        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}

        if plan is None or not plan.strip():
            return _bad_request("Missing required field: 'plan' (non-empty string).")

        # 2) Run your grading / validation pipeline
        try:
            result = run_grader(plan=plan, domain=domain, problem=problem, meta=meta)
        except StudentInputError as e:
            # errors caused by bad student input -> 400
            return _bad_request(str(e))
        except Exception as e:
            # unexpected server error -> 500 (with safe message)
            return _server_error("Internal error during grading.")

        # 3) Return structured JSON result
        return jsonify(result), 200

    @app.post("/grade-file")
    def grade_file():
        """
        Multipart upload:
          - files['plan']    : required (text file)
          - files['domain']  : optional
          - files['problem'] : optional
        """
        # if "plan" not in request.files:
        #     return _bad_request("Upload must include a file part named 'plan'.")

        plan_file = request.files["plan"]
        domain_file = request.files.get("domain")
        problem_file = request.files.get("problem")

        plan = plan_file.read().decode("utf-8", errors="replace")
        domain = domain_file.read().decode("utf-8", errors="replace") if domain_file else None
        problem = problem_file.read().decode("utf-8", errors="replace") if problem_file else None

        try:
            result = run_grader(plan=plan, domain=domain, problem=problem, meta={"source": "upload"})
        except StudentInputError as e:
            return _bad_request(str(e))
        except Exception:
            return _server_error("Internal error during grading.")

        return jsonify(result), 200

    # Global error handler (nicer JSON errors)
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return jsonify({"error": e.name, "message": e.description}), e.code
        return jsonify({"error": "InternalServerError", "message": "Unexpected error"}), 500

    return app


# -----------------------
# Domain model & grading
# -----------------------
@dataclass
class GradeReport:
    ok: bool
    summary: str
    scores: Dict[str, float]
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "summary": self.summary,
            "scores": self.scores,
            "details": self.details,
        }


class StudentInputError(Exception):
    pass


def run_grader(*, plan: str, domain: Optional[str], problem: Optional[str], meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Core grading logic: validate a PDDL plan using the Grader class.
    """
    # --- Basic input checks ---
    if len(plan.strip().splitlines()) == 0:
        raise StudentInputError("Plan file is empty.")
    if domain is None or not domain.strip():
        raise StudentInputError("Domain file is required.")
    if problem is None or not problem.strip():
        raise StudentInputError("Problem file is required.")

    # --- Setup temporary directory for grading ---
    base_folder = tempfile.mkdtemp(prefix="pddl-grader-")
    student_id = str(uuid.uuid4())
    problem_name = meta.get("problem_name", "p01.pddl") # Default problem name if not provided

    try:
        # --- Create the directory structure Grader expects ---
        submission_dir = os.path.join(base_folder, "submissions", student_id)
        reference_dir = os.path.join(base_folder, "reference")
        marking_dir = os.path.join(base_folder, "marking")
        os.makedirs(submission_dir)
        os.makedirs(reference_dir)
        os.makedirs(marking_dir)

        # --- Write submitted files ---
        with open(os.path.join(submission_dir, "domain.pddl"), "w") as f:
            f.write(domain)
        with open(os.path.join(submission_dir, problem_name), "w") as f:
            f.write(problem)
        # The Grader's check_solve expects the plan to be in the marking dir, so we place it there.
        os.makedirs(os.path.join(marking_dir, student_id))
        with open(os.path.join(marking_dir, student_id, f"plan.{problem_name}"), "w") as f:
            f.write(plan)

        # --- Copy reference files (assuming they are in a known location) ---
        # This part is tricky; for now, we'll assume the submitted domain/problem can also serve as reference
        # A real implementation would copy from a secured, standard reference set.
        with open(os.path.join(reference_dir, "domain.pddl"), "w") as f:
            f.write(domain)
        with open(os.path.join(reference_dir, problem_name), "w") as f:
            f.write(problem)

        # --- Run the grader and get the report dictionary ---
        grader = Grader(base_folder)
        report_dict = grader.grade(student_id)

        return report_dict

    finally:
        # --- Clean up the temporary directory ---
        shutil.rmtree(base_folder)


# -----------------------
# Helpers
# -----------------------
def _expect_str(obj: Dict[str, Any], key: str, *, required: bool) -> Optional[str]:
    val = obj.get(key)
    if val is None:
        return None if not required else None
    if not isinstance(val, str):
        raise StudentInputError(f"Field '{key}' must be a string.")
    return val

def _normalize_plan(plan: str) -> str:
    # Very simple normalization demo: trim and collapse multiple blank lines
    lines = [ln.rstrip() for ln in plan.splitlines()]
    return "\n".join(lines).strip()

def _length_penalty(plan: str) -> float:
    # Example: shorter plans slightly preferred but bounded
    n = len([ln for ln in plan.splitlines() if ln.strip()])
    return max(0.0, min(1.0, 1.5 / (1 + 0.05 * n)))

def _bad_request(msg: str):
    return jsonify({"error": "BadRequest", "message": msg}), 400

def _server_error(msg: str):
    return jsonify({"error": "InternalServerError", "message": msg}), 500


# -----------------------
# Entrypoint
# -----------------------
if __name__ == "__main__":
    # DEV defaults: listen on localhost:5000
    port = int(os.environ.get("PORT", "5000"))
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=True)
