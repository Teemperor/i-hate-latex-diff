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

stop_marker = "%diff-off"
start_marker = "%diff-on"

# minted will probably just print out injected code-as is, so ignore it.
ignored_prefixes = [
  "\\mintinline",
  "\\captionof",
  "\\begin",
  start_marker,
  stop_marker,
]


def should_ignore_token(token : str) -> str:
    for prefix in ignored_prefixes:
        if token.startswith(prefix):
            return True
    return False


def make_tokens(lines):
    """
    Creates the latex tokens feed to the diff tool.
    """

    result = lines
    split_on = [" "]

    for splitter in split_on:
        tmp_result = []
        for tmp in result:
            # Split by sep but preserve the sep. This way we can concatenate
            # at the end and recreate the original input.
            tokens = tmp.split(splitter)
            for token in tokens[:-1]:
                tmp_result.append(token + splitter)
            if tokens:
                tmp_result.append(tokens[-1])
        result = tmp_result
    return result

class TokenOutput:
    def __init__(self):
        self.result = ""
        self.last_cmd = None

    def append(self, content):
        self.append_cmd(None, content)

    def append_cmd(self, cmd, content):
        if self.last_cmd == cmd:
            # Just append 
            cmd = None
        else:
            # Make sure the last command was terminated.
            if self.last_cmd:
                if self.result.endswith("\n"):   
                    self.result = self.result[:-1] + cmd_end + "\n"
                else:
                    self.result += cmd_end
            self.last_cmd = cmd
        
        if cmd is None:
            cmd = ""
        self.result += cmd + content

def make_latex_diff(old, new):
    """
    Given two lists of lines, creates a string describing the latex source
    code representing the 'new' changes with any differences highlighted.
    """

    result = TokenOutput()

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

    should_diff = True

    last_code = None

    for token in diff:
        # The first character is a diff marker such as '+', '-' or ' '.
        code = token[0]
        # The raw original input.
        content = token[1:]

        if content.startswith(stop_marker):
            should_diff = False
        if content.startswith(start_marker):
            should_diff = True

        # Some tokens will break latex when we add annotations, so filter them
        # out and just show the text in the 'new' version of the document.
        if should_ignore_token(content):
            if code == "+":
                # Show the token without annotation.
                code = " "
            elif code == "-":
                # Don't emit the token at all so only the addition shows.
                continue

        # True if it's the same change code as before.
        same_code = (code == last_code) if last_code else False

        if ignore_token in token:
            # This is a file indicator, don't use it as it's fake files.
            continue
        elif code == "@":
            # This is an annotation, ignore it.
            continue
        elif code == "-":
            # This was removed, so annotate the latex code.
            if should_diff:
                result.append_cmd(removed_change_cmd, content)
        elif code == "+":
            # This was added, so annotate the latex code.
            if should_diff:
                result.append_cmd(added_change_cmd, content)
            else:
                result.append(content)
        elif code == " ":
            # Unchanged, just copy it over.
            result.append(content)
        else:
            print("Unknown difflib code: " + code)
            sys.exit(1)

    return result.result

def maybe_define_latex_macros(content):
    definitions = r"""
\usepackage{xcolor}
\usepackage[normalem]{ulem}
\renewcommand{\removedChange}[1]{\colorlet{defaultcolor}{.}\color{red}{\sout{#1}}\color{defaultcolor}}
\renewcommand{\addedChange}[1]{\colorlet{defaultcolor}{.}\color{blue}{\uwave{#1}}\color{defaultcolor}}
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
