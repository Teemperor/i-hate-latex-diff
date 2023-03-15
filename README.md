# i-hate-latex-diff

![Status badge](https://github.com/Teemperor/i-hate-latex-diff/actions/workflows/python-app.yml/badge.svg)

This is latex-diff but it at least works for my paper.

```bash
./i-hate-latex-diff.py original-folder new-folder output-folder
```

All `*.tex` files in the `original` and `new` folder will be compared.
`output` contains the same files except for the annotated changes. Afterwards just compile your paper with whatever cursed build system you're already suffering from.

**Available flags:**

* `--nodefine`: Don't inject the default command definitions. You can add your own `removedChange` and `addedChange` definitions.

## FAQ

* *Will this work on my paper?* - Probably no.
* *What's wrong with latex-diff?* - I can't answer this here without exceeding the git file size limitations.