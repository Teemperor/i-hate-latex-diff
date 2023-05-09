# i-hate-latex-diff

![Status badge](https://github.com/Teemperor/i-hate-latex-diff/actions/workflows/python-app.yml/badge.svg)

This is a latex-diff reimplementation but it works with my own paper.

```bash
./i-hate-latex-diff.py original-folder new-folder output-folder
```

All `*.tex` files in the `original` and `new` folder will be compared.
`output` contains the same files except for the annotated changes.
Afterwards just compile your paper with whatever cursed build system you're
already suffering from.
Note that all other files and the directory structure is preserved, so you can
easily diff the output folder to see what the tool has annotated.

**Usage**

The script doesn't try to parse latex which is an unsolvable problem in computer
science. Instead, it just does a plain diff on everything you changed between
files and then annotates the changed tokens with the `removedChange` and
`addedChange` commands.

Now, this also means this script doesn't know if you're in some cursed
latex environment where these commands might misbehave or not compile. So,
to avoid this you can (and should) place custom markers in your changed source
code to disable diffing. You can do this like this:

```
Unchanged latex text here.
%diff-off
\minted{This stuff here changed but commands in minted don't work}
%diff-on
More unchanged latex text.
```

**Available flags:**

* `--nodefine`: Don't inject the default command definitions. You can add your
own `removedChange` and `addedChange` definitions.

* `--verbose`: Spam your stdout. Has useful information, but it also emulates
the LaTeX behavior of spamming my f**** screen with millions of pointless
warnings.

## Tests

Simply run:

```bash
./tests/test.py
```

Each test dir has a `a` directory for the old version, `b` or the new version,
and an `expected` directory for the expected output.

## FAQ

* *Will this work on my paper?* - no.
* *What's wrong with latex-diff?* - I can't answer this here without exceeding
the git file size limitations.
* *Why is this README so salty?* - Because LaTeX was literally created in hell
to punish humanity for creating the atom bomb or something like that.