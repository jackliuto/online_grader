import sys, os
import glob, tabulate

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

    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.reference_loc = os.path.join(base_folder, 'reference')
        self.submissions_loc = os.path.join(base_folder, 'submissions')
        self.marking_loc = os.path.join(base_folder, 'marking')

        # Make sure all three directories exist
        for loc in [self.reference_loc, self.submissions_loc, self.marking_loc]:
            if not os.path.isdir(loc):
                print(f'Error: {loc} does not exist')
                sys.exit(1)

    def check_alignment(self, student_id, prob):
        os.system(f'python3 merge.py {self.reference_loc}/domain.pddl {self.reference_loc}/{prob} {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} {self.marking_loc}/{student_id}/domain.pddl {self.marking_loc}/{student_id}/{prob} > {self.marking_loc}/{student_id}/merge.log 2>&1')
        os.system(f'./plan.sh {self.marking_loc}/{student_id}/plan.{prob}.merged {self.marking_loc}/{student_id}/domain.pddl {self.marking_loc}/{student_id}/{prob} 60 > {self.marking_loc}/{student_id}/planner.{prob}.merged.log 2>&1')
        with open(f'{self.marking_loc}/{student_id}/planner.{prob}.merged.log', 'r') as f:
            mtext = f.read()
            align = 'Search stopped without finding a solution.' in mtext
        if not (align or os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}.merged')):
            print(f'Warning: Alignment failed for {student_id}/{prob}')

        plan = None
        if os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}.merged'):
            with open(f'{self.marking_loc}/{student_id}/plan.{prob}.merged', 'r') as f:
                plan = f.read()
        return (align, plan)

    def check_solve(self, student_id, prob, optimal=False):
        if optimal:
            planner = 'planoptimal.sh'
        else:
            planner = 'plan.sh'
        os.system(f'./{planner} {self.marking_loc}/{student_id}/plan.{prob} {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} 60 > {self.marking_loc}/{student_id}/planner.{prob}.log 2>&1')
        return os.path.isfile(f'{self.marking_loc}/{student_id}/plan.{prob}')

    def check_validate(self, student_id, prob):
        os.system(f'./validate.sh {self.reference_loc}/domain.pddl {self.reference_loc}/{prob} {self.marking_loc}/{student_id}/plan.{prob} > {self.marking_loc}/{student_id}/validate1.{prob}.log 2>&1')
        with open(f'{self.marking_loc}/{student_id}/validate1.{prob}.log', 'r') as f:
            vtext = f.read()
            valid1 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
        os.system(f'./validate.sh {self.submissions_loc}/{student_id}/domain.pddl {self.submissions_loc}/{student_id}/{prob} {self.reference_loc}/plan.{prob} > {self.marking_loc}/{student_id}/validate2.{prob}.log 2>&1')
        with open(f'{self.marking_loc}/{student_id}/validate2.{prob}.log', 'r') as f:
            vtext = f.read()
            valid2 = ('Plan executed successfully' in vtext) and ('Plan valid' in vtext)
        return (valid1, valid2)


    def gradeall(self):
        sdirs = glob.glob(f'{self.submissions_loc}/*')
        for sdir in sdirs:
            student_id = sdir.split('/')[-1]
            self.grade(student_id)

    def grade(self, student_id):
        print(f"Grading {student_id}...")

        if os.path.exists(f'{self.marking_loc}/{student_id}'):
            os.system(f'rm -rf {self.marking_loc}/{student_id}')
        os.mkdir(f'{self.marking_loc}/{student_id}')

        alignment_results = {p: {} for p in self.PROBLEMS}

        print('  finding plans...')
        for prob in alignment_results:
            alignment_results[prob]['solve'] = self.MARK[self.check_solve(student_id, f'{prob}.pddl')]

        print('  validating plans...')
        for prob in alignment_results:
            if alignment_results[prob]['solve'] == self.MARK[True]:
                validates1, validates2 = self.check_validate(student_id, f'{prob}.pddl')
                alignment_results[prob]['validates1'] = self.MARK[validates1]
                alignment_results[prob]['validates2'] = self.MARK[validates2]
            else:
                _, validates2 = self.check_validate(student_id, f'{prob}.pddl')
                alignment_results[prob]['validates1'] = '-'
                alignment_results[prob]['validates2'] = self.MARK[validates2]

        print('  checking theory alignments...')
        mis_alignment_plans = {}
        for prob in alignment_results:
            align, plan = self.check_alignment(student_id, f'{prob}.pddl')
            if plan:
                mis_alignment_plans[prob] = plan
            alignment_results[prob]['aligns'] = self.MARK[align]

        print('  checking for optimal plans...')
        optimal_plan_results = {p: {} for p in self.PLAN_ONLY_PROBLEMS}
        for prob in optimal_plan_results:
            solved = self.check_solve(student_id, f'{prob}.pddl', optimal=True)
            optimal_plan_results[prob]['solve'] = self.MARK[solved]
            if solved:
                with open(f'{self.marking_loc}/{student_id}/plan.{prob}.pddl', 'r') as f:
                    optimal_plan_results[prob]['plan'] = f.read()
            else:
                optimal_plan_results[prob]['plan'] = None

        # Assemble final dictionary
        final_report = {
            'alignment_results': alignment_results,
            'mis_alignment_plans': mis_alignment_plans,
            'optimal_plan_results': optimal_plan_results
        }

        # Still write to file for command-line use, but return dictionary
        with open(f'{self.marking_loc}/{student_id}/grade.txt', 'w', encoding='utf-8') as f:
            import json
            f.write(json.dumps(final_report, indent=2))

        print('Done!\n')
        return final_report

def main():
    if len(sys.argv) != 3:
        print(Grader.USAGE)
        sys.exit(1)
    base_folder = sys.argv[1]
    student_arg = sys.argv[2]

    grader = Grader(base_folder)

    if student_arg == 'all':
        grader.gradeall()
    else:
        grader.grade(student_arg)

if __name__ == '__main__':
    main()
