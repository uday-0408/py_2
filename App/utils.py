def generate_default_function(problem):
    """
    Generates a function skeleton like `def climb_stairs(n):` with placeholder logic.
    """
    function_name = problem.slug.replace("-", "_")
    return f"def {function_name}(n):\n    # Write your logic here\n    pass\n"


def generate_runner_code(problem, mode="run"):
    function_name = problem.slug.replace("-", "_")
    runner = "\n\nif __name__ == '__main__':\n"
    cases = []

    if mode == "run":
        try:
            examples = problem.examples_group.examples
        except Exception as e:
            print(f"Error fetching examples: {e}")
            examples = []

        for example in examples:
            input_val = example.get("input") or example.get("input_example")
            expected_output = example.get("output") or example.get("output_example")

            if input_val is None or expected_output is None:
                continue

            cases.append({"input": input_val, "expected": expected_output})
            runner += f"    print({function_name}({input_val}))  # Expected: {expected_output}\n"

    elif mode == "submit":
        try:
            test_cases = problem.testcase_group.test_cases
        except Exception as e:
            print(f"Error fetching test cases: {e}")
            test_cases = []

        for case in test_cases:
            input_val = case.get("input") or case.get("input_example")
            expected_output = case.get("output") or case.get("output_example")

            if input_val is None or expected_output is None:
                continue

            cases.append({"input": input_val, "expected": expected_output})
            runner += f"    print({function_name}({input_val}))\n"

    if not cases:
        print("⚠️ No cases were added! Runner will be empty.")
        runner += "    print('No test cases found')\n"

    print("========== GENERATED RUNNER CODE ==========")
    print(runner)
    print("========== END RUNNER CODE ==========")

    return runner, cases


def compare_outputs(raw_output, cases):
    """
    Compares each line of output with expected values and returns:
    - list of results (with pass/fail, input, expected, got)
    - bool for all passed
    - failed test case index (1-based)
    """
    outputs = raw_output.strip().split("\n")
    results = []
    all_passed = True
    failed_case_number = None

    for idx, case in enumerate(cases):
        got = outputs[idx].strip() if idx < len(outputs) else ""
        expected = str(case["expected"]).strip()
        passed = got == expected

        if not passed and failed_case_number is None:
            failed_case_number = idx + 1
            all_passed = False

        results.append(
            {
                "input": case["input"],
                "expected": expected,
                "output": got,
                "passed": passed,
            }
        )

    return results, all_passed, failed_case_number
