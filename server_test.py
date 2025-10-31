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

from grader import Grader


REFERENCE_LOC = "data/reference"

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
          "domain": "<PDDL domain text>",      # required
          "problem": "<PDDL problem text>",    # required
          "problem_id": "1|2|3"                # required
        }
        """
        # 1) Parse & validate inputs
        try:
            payload = request.get_json(force=True, silent=False)
        except Exception:
            return _bad_request("Body must be valid JSON with domain/problem/problem_id.")

        domain = _expect_str(payload, "domain", required=True)
        problem = _expect_str(payload, "problem", required=True)
        problem_id = _expect_str(payload, "problem_id", required=True)

        if domain is None or not domain.strip():
            return _bad_request("Missing required field: 'domain' (non-empty string).")
        if problem is None or not problem.strip():
            return _bad_request("Missing required field: 'problem' (non-empty string).")
        if problem_id not in ["1", "2", "3"]:
            return _bad_request("Field 'problem_id' must be '1', '2', or '3'.")

        # 2) Run your grading / validation pipeline
        try:
            result = run_grader(domain=domain, problem=problem, problem_id=problem_id)
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
        Accepts either JSON or multipart form-data.
        - JSON body fields: 'domain' (required), 'problem' (required), 'problem_id' (required '1'|'2'|'3')
        - Multipart upload:
            files['domain']  : required
            files['problem'] : required
            form['problem_id']: required ('1', '2', or '3')
        """
        plan = None
        domain = None
        problem = None
        problem_id = None

        if request.is_json:
            try:
                payload = request.get_json(force=True, silent=False)
            except Exception:
                return _bad_request("Body must be valid JSON with domain/problem/problem_id.")
            domain = payload.get("domain")
            problem = payload.get("problem")
            problem_id = payload.get("problem_id")
        else:
            # Multipart form-data path
            domain_file = request.files.get("domain")
            problem_file = request.files.get("problem")
            problem_id = request.form.get("problem_id")

            if domain_file:
                domain = domain_file.read().decode("utf-8", errors="replace")
            if problem_file:
                problem = problem_file.read().decode("utf-8", errors="replace")

        # Basic validations aligned with test client
        if domain is None or not str(domain).strip():
            return _bad_request("Missing required field: 'domain'.")
        if problem is None or not str(problem).strip():
            return _bad_request("Missing required field: 'problem'.")
        if not problem_id or problem_id not in ["1", "2", "3"]:
            return _bad_request("Field 'problem_id' must be '1', '2', or '3'.")

        try:
            result = run_grader(domain=domain, problem=problem, problem_id=problem_id)
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


def run_grader(*, domain: Optional[str], problem: Optional[str], problem_id: str) -> Dict[str, Any]:
    """
    Core grading logic: validate a PDDL plan using the Grader class.
    """
    # --- Basic input checks ---
    if domain is None or not domain.strip():
        raise StudentInputError("Domain file is required.")
    if problem is None or not problem.strip():
        raise StudentInputError("Problem file is required.")

    # --- Setup temporary directory for grading ---
    reference_dir = REFERENCE_LOC
    grader = Grader(reference_dir)

    # 1) Generate a plan using submitted domain/problem
    plan_gen = grader.generate_plan(domain, problem, timeout=30, optimal=False)
    if not plan_gen.get("ok"):
        return {
            "ok": False,
            "error": "Plan generation failed",
            "planning": plan_gen,
        }
    plan_text = plan_gen.get("plan", "")

    # 2) Validate both directions
    validation = grader.validate_submission(domain, problem, plan_text, problem_id)

    # 3) Check alignment
    alignment = grader.check_alignment(domain, problem, problem_id)

    return {
        "ok": bool(validation.get("student_plan_on_reference", {}).get("ok") and validation.get("reference_plan_on_student", {}).get("ok")),
        "planning": plan_gen,
        "validation": validation,
        "alignment": alignment,
    }


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
