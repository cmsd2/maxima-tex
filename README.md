# maxima-tex

Run [Maxima](https://maxima.sourceforge.io) from Python and show the result as
LaTeX. Made for Jupyter notebooks and Quarto documents, where a code cell can
then display a computer-algebra result as properly typeset maths, in both HTML
and PDF output.

````markdown
```{python}
#| echo: false
from maxima_tex import maxima
maxima("integrate(x*lambda*exp(-lambda*x), x, 0, inf)",
       setup="assume(lambda > 0)", lhs="E(X)")
```
````

renders as

$$ E(X) = \frac{1}{\lambda} $$

## Install

```sh
uv add "maxima-tex[notebook] @ git+https://github.com/cmsd2/maxima-tex"
# or
pip install "maxima-tex[notebook] @ git+https://github.com/cmsd2/maxima-tex"
```

The `notebook` extra pulls in IPython, which `maxima()` needs to display its
result. Any Jupyter kernel already has it. `maxima_tex()` needs nothing but
Python.

Maxima itself must be installed: `brew install maxima`, `apt install maxima`,
or the Windows installer from SourceForge. The package looks for the
executable in the `MAXIMA` environment variable, then on `PATH`. On Windows,
`maxima` is `maxima.bat` in the install's `bin` folder.

## Use

| Call | Returns |
|---|---|
| `maxima_tex(expr, setup="")` | the LaTeX of the value of `expr`, as a string |
| `maxima(expr, setup="", lhs=None)` | an IPython `Markdown` object holding `$$ lhs = value $$` |

- `expr` runs as a top-level statement, so evaluation flags work:
  `"sum(r^k, k, 0, n-1), simpsum"`.
- `setup` runs first and may hold several statements:
  `"load(simplify_sum)$ assume(m > 0)"`.
- Each call starts a fresh Maxima process, so cells never share state. Put
  everything a result depends on into `setup`.
- Use ASCII names (`lambda`, not `λ`). Maxima passes Unicode straight through
  to TeX, where it may not typeset.
- Matrices come out as `\begin{pmatrix} 1&2 \\ 3&4 \end{pmatrix}`. Maxima's
  own `tex()` wraps them in an `\ifx` test for plain TeX, which MathJax can't
  read, so HTML output would show an error in place of the matrix.

**Errors raise.** Maxima carries on after an error and leaves `%` holding an
earlier result, so a naive wrapper can quietly show the wrong answer. Any
Maxima error message raises `MaximaError` instead, with Maxima's output in
the message.

## With Quarto's freeze

Under `execute: freeze: auto`, Quarto stores computed results in `_freeze/`.
Commit that folder, and machines without Maxima can still render the
document.

## Licence

[MIT](LICENSE).
