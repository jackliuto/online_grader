# TA Grader

This folder contains tools for grading and validating PDDL student submissions. It is intended for use by teaching assistants and instructors to automate the assessment of planning assignments.

## Folder Structure
- `grade.py` — Main grading script for batch evaluation of student submissions.
- `merge.py` — Utility for merging and aligning domains/problems.
- `plan.sh`, `planoptimal.sh` — Scripts for generating plans using Fast Downward .
- `validate.sh` — Script for validating plans.
- `fast-downward.sif` — Singularity image for the Fast Downward planner (required).
- `submissions/` — Contains student submission folders and files.
- `val/` — Contains VAL binaries for plan validation.

## Requirements
- Python 3.11
- Python packages:
  - tarski
  - antlr4-python3-runtime
  - tabulate
- Bash shell
- The scripts `plan.sh`, `planoptimal.sh`, `merge.py`, and `validate.sh` (included in this folder)
- The file `fast-downward.sif` (must be present in this folder for planning to work)
- Ensure all scripts are executable: `chmod +x plan.sh planoptimal.sh validate.sh`

## Usage
Run all commands from within the `ta_grader` directory.

### 1. Grading Student Submissions
The main workflow is to use `grade.py` to grade all or specific student submissions in the `submissions/` folder.

```
python3 grade.py <base_folder> [<student_id>|all]
```
- `<base_folder>`: Path to the assignment folder (e.g., `submissions/queens_example`)
- `<student_id>`: (Optional) Grade a specific student. Use `all` to grade all students in the folder.

**Example:**
```
python3 grade.py submissions/queens_example 1
python3 grade.py submissions/queens_example all
```

### 2. Merging and Alignment
You can use `merge.py` directly to merge and align domains/problems:
```
python3 merge.py <ref_domain> <ref_problem> <sub_domain> <sub_problem> <out_domain> <out_problem>
```

### 3. Plan Generation
Generate a plan using the provided scripts:
```
./plan.sh <output_plan> <domain.pddl> <problem.pddl> <timeout_seconds>
./planoptimal.sh <output_plan> <domain.pddl> <problem.pddl> <timeout_seconds>
```

### 4. Plan Validation
Validate a plan:
```
./validate.sh <domain.pddl> <problem.pddl> <plan_file>
```

## Notes
- `fast-downward.sif` must be present in this folder for planning to work.
- All scripts should be executable. If not, run `chmod +x scriptname.sh`.
- The `val/` folder contains binaries for plan validation; ensure they are compatible with your system.
- Output and logs are typically saved in the marking directories within each assignment folder.
- If you encounter permission or execution errors, check script permissions and Singularity installation. 