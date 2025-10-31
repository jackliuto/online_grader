import sys, os
import glob, tabulate
import subprocess, tempfile
import time
from pathlib import Path

class Grader:
    USAGE = """
    Usage: python3 grade.py <base_folder> [<student_id>|all]
    """

    # Change to reflect the list of problems for testing alignment
    PROBLEMS = ['p01', 'p02', 'p03']

    # Problems for just finding a plan
    PLAN_ONLY_PROBLEMS = ['p04']

    MARK = {
        False: 'fail',
        True: 'pass'
    }

    def __init__(self, reference_folder):
        
        self.reference_folder = reference_folder


        
        # self.reference_loc = os.path.join(base_folder, 'reference')
        # self.submissions_loc = os.path.join(base_folder, 'submissions')
        # self.marking_loc = os.path.join(base_folder, 'marking')

        # # Make sure all three directories exist
        # for loc in [self.reference_loc, self.submissions_loc, self.marking_loc]:
        #     if not os.path.isdir(loc):
        #         print(f'Error: {loc} does not exist')
        #         sys.exit(1)

    # def check_alignment(self, student_id, prob):
    #     os.system(f'python3 merge.py {self.reference_loc}/domain.pddl {self.reference_loc}/{prob} {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} {self.marking_loc}/{student_id}/domain.pddl {self.marking_loc}/{student_id}/{prob} > {self.marking_loc}/{student_id}/merge.log 2>&1')
    #     os.system(f'./plan.sh {self.marking_loc}/{student_id}/plan.{prob}.merged {self.marking_loc}/{student_id}/domain.pddl {self.marking_loc}/{student_id}/{prob} 60 > {self.marking_loc}/{student_id}/planner.{prob}.merged.log 2>&1')
    #     with open(f'{self.marking_loc}/{student_id}/planner.{prob}.merged.log', 'r') as f:
    #         mtext = f.read()
    #         align = 'Search stopped without finding a solution.' in mtext
    #     if not (align or os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}.merged')):
    #         print(f'Warning: Alignment failed for {student_id}/{prob}')

    #     plan = None
    #     if os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}.merged'):
    #         with open(f'{self.marking_loc}/{student_id}/plan.{prob}.merged', 'r') as f:
    #             plan = f.read()
    #     return (align, plan)

    # def check_solve(self, student_id, prob, optimal=False):
    #     if optimal:
    #         planner = 'planoptimal.sh'
    #     else:
    #         planner = 'plan.sh'
    #     os.system(f'./{planner} {self.marking_loc}/{student_id}/plan.{prob} {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} 60 > {self.marking_loc}/{student_id}/planner.{prob}.log 2>&1')
    #     return os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}')

    # def check_validate(self, student_id, prob):
    #     os.system(f'./validate.sh {self.reference_loc}/domain.pddl {self.reference_loc}/{prob} {self.marking_loc}/{student_id}/plan.{prob} > {self.marking_loc}/{student_id}/validate1.{prob}.log 2>&1')
    #     with open(f'{self.marking_loc}/{student_id}/validate1.{prob}.log', 'r') as f:
    #         vtext = f.read()
    #         valid1 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    #     os.system(f'./validate.sh {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} {self.reference_loc}/plan.{prob} > {self.marking_loc}/{student_id}/validate2.{prob}.log 2>&1')
    #     with open(f'{self.marking_loc}/{student_id}/validate2.{prob}.log', 'r') as f:
    #         vtext = f.read()
    #         valid2 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
    #     return (valid1, valid2)

    def validate_submission(self, domain_text, problem_text, plan_text, problem_id, timeout=60):
        """
        Run two validations:
        1) Student plan on reference domain/problem.
        2) Reference plan on student domain/problem.

        Returns a dict with booleans and logs for both checks.
        """
        # Resolve reference file paths
        ref_domain = os.path.join(self.reference_folder, "domain.pddl")
        ref_problem = os.path.join(self.reference_folder, f"p0{problem_id}.pddl")
        ref_plan = os.path.join(self.reference_folder, f"plan.p0{problem_id}.pddl")

        if not os.path.isfile(ref_domain):
            raise FileNotFoundError(f"Reference domain not found: {ref_domain}")
        if not os.path.isfile(ref_problem):
            raise FileNotFoundError(f"Reference problem not found: {ref_problem}")
        if not os.path.isfile(ref_plan):
            raise FileNotFoundError(f"Reference plan not found: {ref_plan}")

        with tempfile.TemporaryDirectory(prefix="pddl-validate-") as tmp:
            tmpdir = Path(tmp)
            # Write student texts
            stu_domain = tmpdir / "student.domain.pddl"
            stu_problem = tmpdir / "student.problem.pddl"
            stu_plan = tmpdir / "student.plan.pddl"

            stu_domain.write_text(domain_text or "", encoding="utf-8")
            stu_problem.write_text(problem_text or "", encoding="utf-8")
            stu_plan.write_text(plan_text or "", encoding="utf-8")

            # 1) Student plan on reference files
            proc1 = subprocess.run(
                ["./validate.sh", ref_domain, ref_problem, str(stu_plan)],
                capture_output=True, text=True, timeout=timeout
            )
            out1 = proc1.stdout
            ok1 = "Plan executed successfully" in out1

            # 2) Reference plan on student files
            proc2 = subprocess.run(
                ["./validate.sh", str(stu_domain), str(stu_problem), ref_plan],
                capture_output=True, text=True, timeout=timeout
            )
            out2 = proc2.stdout
            ok2 = "Plan executed successfully" in out2

            return {
                "student_plan_on_reference": {
                    "ok": ok1,
                    "returncode": proc1.returncode,
                    "stdout": proc1.stdout or "",
                    "stderr": proc1.stderr or "",
                },
                "reference_plan_on_student": {
                    "ok": ok2,
                    "returncode": proc2.returncode,
                    "stdout": proc2.stdout or "",
                    "stderr": proc2.stderr or "",
                },
            }

    def generate_plan(self, domain_text: str, problem_text: str, *, timeout: int = 30, optimal: bool = False):
        """
        Generate a plan using the provided domain/problem texts.
        Writes inputs to a temp dir and runs plan.sh (or planoptimal.sh).

        Returns a dict with keys: ok, plan (if found), returncode, stdout, stderr.
        """
        planner = "./planoptimal.sh" if optimal else "./plan.sh"
        with tempfile.TemporaryDirectory(prefix="pddl-plan-") as tmp:
            tmpdir = Path(tmp)
            dpath = tmpdir / "domain.pddl"
            ppath = tmpdir / "problem.pddl"
            out_plan = tmpdir / "plan.pddl"

            dpath.write_text(domain_text or "", encoding="utf-8")
            ppath.write_text(problem_text or "", encoding="utf-8")

            if not domain_text or not domain_text.strip():
                raise ValueError("domain_text is empty")
            if not problem_text or not problem_text.strip():
                raise ValueError("problem_text is empty")

            proc = subprocess.run(
                [planner, str(out_plan), str(dpath), str(ppath), str(timeout)],
                capture_output=True, text=True, timeout=timeout + 5
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            plan_text = out_plan.read_text(encoding="utf-8") if out_plan.exists() else ""
            ok = out_plan.exists() and bool(plan_text.strip())
            return {
                "ok": ok,
                "plan": plan_text,
                "returncode": proc.returncode,
                "stdout": stdout,
                "stderr": stderr,
            }

    def check_alignment(self, student_domain_text: str, student_problem_text: str, problem_id: str, *, timeout: int = 60):
        """
        Merge reference and student domain/problem via merge.py, then plan on the merged
        files. Logic mirrors server.py's check_alignment:
        - If merge log contains 'Error', treat as merge failure (non-fatal to server, but alignment_ok=False).
        - Run planner and read its log:
            * If planner log contains 'Search stopped without finding a solution.', then alignment_ok=True.
            * If a plan file is produced, alignment_ok=False and return that plan.
            * If neither, alignment failed; include error details.
        Returns a diagnostics dict similar in spirit to (align, plan, error).
        """
        # Reference paths
        ref_domain = os.path.join(self.reference_folder, "domain.pddl")
        ref_problem = os.path.join(self.reference_folder, f"p0{problem_id}.pddl")
        if not os.path.isfile(ref_domain):
            raise FileNotFoundError(f"Reference domain not found: {ref_domain}")
        if not os.path.isfile(ref_problem):
            raise FileNotFoundError(f"Reference problem not found: {ref_problem}")

        merge_py = os.path.join(os.path.dirname(__file__), "merge.py")
        if not os.path.isfile(merge_py):
            raise FileNotFoundError(f"merge.py not found at {merge_py}")

        with tempfile.TemporaryDirectory(prefix="pddl-merge-") as tmp:
            tmpdir = Path(tmp)
            # Write student inputs
            stu_domain = tmpdir / "student.domain.pddl"
            stu_problem = tmpdir / "student.problem.pddl"
            stu_domain.write_text(student_domain_text or "", encoding="utf-8")
            stu_problem.write_text(student_problem_text or "", encoding="utf-8")

            merged_domain = tmpdir / "merged.domain.pddl"
            merged_problem = tmpdir / "merged.problem.pddl"
            plan_out = tmpdir / "merged.plan"
            plan_log = tmpdir / "plan.merged.log"
            merge_log = tmpdir / "merge.merged.log"

            # No persistent debug artifacts

            # 1) Merge and write logs
            try:
                merge_proc = subprocess.run(
                    ["python3", merge_py, ref_domain, ref_problem, str(stu_domain), str(stu_problem), str(merged_domain), str(merged_problem)],
                    capture_output=True, text=True, timeout=timeout
                )
                (merge_log).write_text((merge_proc.stdout or "") + ("\n" + merge_proc.stderr if merge_proc.stderr else ""), encoding="utf-8")
                pass
            except Exception as e:
                return {
                    "alignment_ok": False,
                    "mis_alignment_plan": "",
                    "error": f"merge failed: {e}",
                    "merge_log": "",
                    "plan_log": "",
                    "timed_out": False,
                    "duration_sec": 0.0,
                }

            # Check the merge file for an error message
            mtext = (merge_log.read_text(encoding="utf-8") if merge_log.exists() else "")
            if "Error" in mtext:
                return {
                    "alignment_ok": False,
                    "mis_alignment_plan": "",
                    "error": "Merge failed",
                    "merge_log": mtext,
                    "plan_log": "",
                    "timed_out": False,
                    "duration_sec": 0.0,
                    "debug_dir": str(debug_dir),
                }

            # 2) Plan on merged
            planner = "./plan.sh"
            t0 = time.time()
            plan_proc = subprocess.run(
                [planner, str(plan_out), str(merged_domain), str(merged_problem), f"{timeout}s"],
                capture_output=True, text=True, timeout=timeout + 5
            )
            dur = time.time() - t0
            # Write plan log
            (plan_log).write_text((plan_proc.stdout or "") + ("\n" + plan_proc.stderr if plan_proc.stderr else ""), encoding="utf-8")
            # No persistent debug artifacts

            # Adding 3s just because the planner cuts short
            if dur + 3 > timeout:
                return {
                    "alignment_ok": False,
                    "mis_alignment_plan": "",
                    "error": "Alignment timed out. This may indicate everything is fine.",
                    "merge_log": mtext,
                    "plan_log": plan_log.read_text(encoding="utf-8") if plan_log.exists() else "",
                    "timed_out": True,
                    "duration_sec": dur,
                }

            # Check planner output for failure message
            plog = plan_log.read_text(encoding="utf-8") if plan_log.exists() else ""
            align = 'Search stopped without finding a solution' in plog

            # If neither aligned nor plan file exists -> alignment step failed; attach error
            error_text = None
            if not (align or plan_out.exists()):
                error_text = mtext

            mis_plan_text = plan_out.read_text(encoding="utf-8") if plan_out.exists() else ""

            return {
                "alignment_ok": bool(align),
                "mis_alignment_plan": mis_plan_text if plan_out.exists() else "",
                "error": error_text,
                "merge_log": mtext,
                "plan_log": plog,
                "timed_out": False,
                "duration_sec": dur,
            }

    # def gradeall(self):
    #     sdirs = glob.glob(f'{self.submissions_loc}/*')
    #     for sdir in sdirs:
    #         student_id = sdir.split('/')[-1]
    #         self.grade(student_id)

    # def grade(self, student_id, problem_name='p01.pddl'):
    #     """Runs the core grading logic for a single problem."""
    #     print(f"Grading {student_id} for problem {problem_name}...")

    #     marking_dir = os.path.join(self.marking_loc, student_id)
    #     if os.path.exists(marking_dir):
    #         os.system(f'rm -rf {marking_dir}')
    #     os.mkdir(marking_dir)

    #     # 1. & 2. Cross-validation
    #     print('  Cross-validating plans...')
    #     valid1, valid2 = self.check_validate(student_id, problem_name)

    #     # 3. Check alignment
    #     print('  Checking theory alignment...')
    #     align, mis_alignment_plan = self.check_alignment(student_id, problem_name)

    #     # Assemble final dictionary
    #     final_report = {
    #         'problem': problem_name,
    #         'student_plan_on_reference_files': self.MARK[valid1],
    #         'reference_plan_on_student_files': self.MARK[valid2],
    #         'alignment': {
    #             'result': self.MARK[align],
    #             'mis_alignment_plan': mis_alignment_plan
    #         }
    #     }

    #     # Still write a file for debugging/logging
    #     with open(os.path.join(marking_dir, 'grade.json'), 'w', encoding='utf-8') as f:
    #         import json
    #         f.write(json.dumps(final_report, indent=2))

    #     print('Done!\n')
    #     return final_report

def main():
    pass
    # if len(sys.argv) != 3:
    #     print(Grader.USAGE)
    #     sys.exit(1)
    # base_folder = sys.argv[1]
    # student_arg = sys.argv[2]

    # grader = Grader(base_folder)

    # if student_arg == 'all':
    #     grader.gradeall()
    # else:
    #     grader.grade(student_arg)

if __name__ == '__main__':
    main()
