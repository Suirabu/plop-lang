#!/usr/bin/python3
from subprocess import run
import glob

test_paths = glob.glob("tests/*.plop")
text_paths = glob.glob("tests/*.txt")

print(f"Running {len(test_paths)} tests in 'tests/'")
print("")

def pass_test(test_path):
    print(f"\033[32mPASS\033[0m {test_path}")

def fail_test(test_path):
    print(f"\033[31mFAIL\033[0m {test_path}")

for path in test_paths:
    pr = run([ "./plop.py", path ], capture_output=True)
    
    text_path = path.rsplit('.', 1)[0] + ".txt"

    # If an expected output file exists, test execution by output
    if text_path in text_paths:
        expected_file = open(text_path, "r")
        expected = expected_file.read()
        expected_file.close()

        output = pr.stdout.decode("utf-8")

        if output == expected:
            pass_test(path)
        else:
            fail_test(path)
    # ...otherwise test program by exit status
    else:
        if pr.returncode == 0:
            pass_test(path)
        else:
            fail_test(path)
