#!/usr/bin/env python3

import os
import subprocess as sp
import tempfile
import os.path as path
import sys

tests = []

script_dir = os.path.dirname(os.path.realpath(__file__))
diff_path = script_dir + "/../i-hate-latex-diff.py"

if len(tests) == 0:
    for test in os.listdir(script_dir):
        if os.path.exists(path.join(script_dir, test, "expected")):
            tests.append(path.join(script_dir, test))

def run_test(directory):
    with tempfile.TemporaryDirectory() as tmpdir:
        sp.check_call([diff_path,
                       path.join(directory, "a"),
                       path.join(directory, "b"),
                       tmpdir])
        
        if len(os.listdir(tmpdir)) == 0:
            return "Output folder was empty"

        diff_result = sp.run(["diff", "-r", "-U1", tmpdir, directory + "/expected"], capture_output=True)
        if diff_result.returncode == 0:
            return None
        return "Wrong output:\n" + diff_result.stdout.decode("utf-8")

for test in tests:
    sys.stdout.write("Running test " + test + ": ")
    error = run_test(test)
    if error:
        print(error)
    else:
        print("OK")