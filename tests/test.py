#!/usr/bin/env python3

import argparse
import os
import subprocess as sp
import tempfile
import shutil
import os.path as path
import sys

tests = []

script_dir = os.path.dirname(os.path.realpath(__file__))
diff_path = script_dir + "/../i-hate-latex-diff.py"


class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    PASS = BOLD + GREEN
    FAIL = BOLD + RED


parser = argparse.ArgumentParser(prog="test", description="Runs the tests")
parser.add_argument(
    "--fixup", action="store_true", help="Overwrites expected with current test results"
)
parser.add_argument("--quiet", action="store_true", help="Hides verbose output")
args = parser.parse_args()

if len(tests) == 0:
    for test in os.listdir(script_dir):
        if os.path.exists(path.join(script_dir, test, "expected")):
            tests.append(path.join(script_dir, test))


def run_test(directory):
    with tempfile.TemporaryDirectory() as tmpdir:
        sp.check_call(
            [diff_path, "--nodefine", path.join(directory, "a"), path.join(directory, "b"), tmpdir]
        )

        if len(os.listdir(tmpdir)) == 0:
            return "Output folder was empty"

        expected_dir = path.join(directory, "expected")
        diff_result = sp.run(
            ["diff", "-r", "-U1", tmpdir, expected_dir], capture_output=True
        )
        if diff_result.returncode == 0:
            return None
        if args.fixup:
            shutil.copytree(tmpdir, expected_dir, dirs_exist_ok=True)
            return "Fixed up tests"
        return "Wrong output:\n" + diff_result.stdout.decode("utf-8")


print("Running {num} tests".format(num=len(tests)))
had_error = False
for test in tests:
    test_name = os.path.basename(test)
    sys.stdout.write("Test " + test_name + ": ")
    error = run_test(test)
    if error:
        had_error = True
        print(Color.FAIL + "FAIL" + Color.END)
        if not args.quiet:
            print(error)
    else:
        print(Color.PASS + " OK " + Color.END)

if had_error:
    sys.exit(1)