#!/usr/bin/env python3

import argparse
import os
import glob
import shutil
import sys
import difflib
import os.path as path


def collect_latex_files(folder):
    result = glob.glob("*.tex", root_dir=folder)
    return result


def get_lines(filename):
    with open(filename) as f:
        return f.readlines()


def overwrite_contents(filename, contents):
    with open(filename, "w") as f:
        return f.write(contents)

added_change_cmd = "\\addedChange{"
removed_change_cmd = "\\removedChange{"
cmd_end = "}"
ignore_token = "IGNORETHISLINE"

def make_latex_diff(old, new):
    result = []
    diff = difflib.unified_diff(old, new, n=10000, fromfile=ignore_token,
                                tofile=ignore_token)

    for line in diff:
        code = line[0]
        content = line[1:-1]
        to_add = ""

        if ignore_token in line:
            continue
        elif code == "@":
            continue
        elif code == "-":
            to_add = removed_change_cmd + content + cmd_end
        elif code == "+":
            to_add = added_change_cmd + content + cmd_end
        elif code == " ":
            to_add = content
        else:
            print("Unknown difflib code: " + code)
            sys.exit(1)
        result.append(to_add)

    return "\n".join(result) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="i-hate-latex-diff",
        description="Who the fuck made latex",
        epilog="What a messed up piece of shit",
    )
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("output")
    args = parser.parse_args()

    if os.path.exists(args.output):
        if len(os.listdir(args.output)) != 0:
            print(
                "Output folder " + args.output + " exists. Not going to overwrite this."
            )
            sys.exit(1)
    shutil.copytree(args.new, args.output, dirs_exist_ok=True)

    expected = collect_latex_files(args.old)
    for latex_file in expected:
        print("Inspecting " + latex_file)
        old_file = path.join(args.old, latex_file)
        new_file = path.join(args.new, latex_file)
        new_content = make_latex_diff(get_lines(old_file), get_lines(new_file))
        overwrite_contents(path.join(args.output, latex_file), new_content)
