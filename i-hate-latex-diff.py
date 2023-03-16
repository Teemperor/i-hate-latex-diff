#!/usr/bin/env python3

import argparse
import os
import filecmp
import glob
import shutil
import sys
import difflib
import os.path as path
from pathlib import Path

# 
def collect_latex_files(folder):
    """
    Searches the folder for latex files. Returns their paths relative to the
    specified folder.
    """
    result = []
    for path in Path(folder).rglob('*.tex'):
        result.append(str(path.relative_to(folder)))
    return result


def get_lines(filename):
    """ Returns all lines in the given file. """
    with open(filename) as f:
        return f.readlines()


def overwrite_contents(filename, contents):
    """ Overwrites the file contents of the given file. """
    with open(filename, "w") as f:
        return f.write(contents)


# The macro that wraps additions.
added_change_cmd = "\\addedChange{"
# The macro that wraps removals.
removed_change_cmd = "\\removedChange{"
# How to terminate the macros above.
cmd_end = "}"


def surround_with_cmd(cmd, content):
    """ Returns the given content wrapped in the given latex command. """
    if content.endswith("\n"):
        return cmd + content[:-1] + cmd_end + "\n"
    return cmd + content + cmd_end


def make_tokens(lines):
    """
    Creates the latex tokens feed to the diff tool.
    """

    result = []
    for line in lines:
        # Split by space but preserve the space. This way we can concatenate
        # at the end and recreate the original input.
        tokens = line.split(" ")
        for token in tokens[:-1]:
            result.append(token + " ")
        if tokens:
            result.append(tokens[-1])
    return result


def make_latex_diff(old, new):
    """
    Given two lists of lines, creates a string describing the latex source
    code representing the 'new' changes with any differences highlighted.
    """

    result = ""

    # Turn the lines into a set of (space-delimited) tokens.
    old_tokens = make_tokens(old)
    new_tokens = make_tokens(new)

    # Ignore the file name markers by giving the file names this weird name.
    # We can filter for this later.
    ignore_token = "IGNORE_THIS_LINE_BECAUSE_ITS_A_FILE_MARKER"

    # Diff context should be large enough to always contain the whole document.
    context = len(old_tokens) + len(new_tokens)

    # Create a diff that contains the whole file in the context.
    diff = difflib.unified_diff(
        old_tokens,
        new_tokens,
        n=context,
        fromfile=ignore_token,
        tofile=ignore_token,
        lineterm="",
    )

    for token in diff:
        # The first character is a diff marker such as '+', '-' or ' '.
        code = token[0]
        # The raw original input.
        content = token[1:]
        # What should be added to the result for this token.
        to_add = ""

        if ignore_token in token:
            # This is a file indicator, don't use it as it's fake files.
            continue
        elif code == "@":
            # This is an annotation, ignore it.
            continue
        elif code == "-":
            # This was removed, so annotate the latex code.
            to_add = surround_with_cmd(removed_change_cmd, content)
        elif code == "+":
            # This was added, so annotate the latex code.
            to_add = surround_with_cmd(added_change_cmd, content)
        elif code == " ":
            # Unchanged, just copy it over.
            to_add = content
        else:
            print("Unknown difflib code: " + code)
            sys.exit(1)
        result += to_add

    return result

def maybe_define_latex_macros(content):
    definitions = r"""
\usepackage{xcolor}
\usepackage[normalem]{ulem}
\newcommand{\removedChange}[1]{\textcolor{red}{\sout{#1}}}
\newcommand{\addedChange}[1]{\textcolor{blue}{\uwave{#1}}}
    """
    token = r"""\begin{document}"""

    return content.replace(token, definitions + token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="i-hate-latex-diff",
        description="Who the fuck made latex",
        epilog="What a messed up piece of shit",
    )
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("output")
    parser.add_argument("--nodefine", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False)
    args = parser.parse_args()
    verbose = args.verbose

    if os.path.exists(args.output):
        if len(os.listdir(args.output)) != 0:
            print("Output folder " + args.output + " exists.")
            print("Not going to overwrite this.")
            sys.exit(1)
    shutil.copytree(args.new, args.output, dirs_exist_ok=True)

    expected = collect_latex_files(args.old)
    for latex_file in expected:
        if verbose:
            print("Processing " + latex_file)
        old_file = path.join(args.old, latex_file)
        new_file = path.join(args.new, latex_file)

        # Determine the new file contents.
        new_content = None
        if filecmp.cmp(old_file, new_file):
            # If the files are equal, just read the file contents as-is.
            if verbose:
                print("Skipping equial files " + latex_file)
            new_content = "".join(get_lines(new_file))
        else:
            # Otherwise do a proper diff on different file contents.
            new_content = make_latex_diff(get_lines(old_file), get_lines(new_file))
        # Inject the macro definitions for changes (unless disabled via a flag).
        if not args.nodefine:
            new_content = maybe_define_latex_macros(new_content)
        overwrite_contents(path.join(args.output, latex_file), new_content)
