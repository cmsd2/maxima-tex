"""Run Maxima from Python and get the result as LaTeX.

    from maxima_tex import maxima
    maxima("integrate(x*exp(-x), x, 0, inf)", lhs="E(X)")

In a Jupyter or Quarto code cell, maxima() displays the result as display
maths, which renders in both HTML and PDF output. maxima_tex() returns the
LaTeX string instead, for use anywhere.

Each call runs one expression in a fresh Maxima process, so cells don't share
state. Maxima is found through the MAXIMA environment variable if set,
otherwise on PATH.
"""

import os
import shutil
import subprocess

__all__ = ["maxima", "maxima_tex", "MaximaError"]
__version__ = "0.1.0"

_MARK = "@@maxima-tex@@"


class MaximaError(RuntimeError):
    """Maxima reported an error, or couldn't be run at all."""


def _executable():
    exe = os.environ.get("MAXIMA") or shutil.which("maxima")
    if not exe:
        raise MaximaError("maxima is not on PATH; install it or set MAXIMA")
    return exe


def maxima_tex(expr, setup="", timeout=120):
    """LaTeX for the value of a Maxima expression.

    `expr` runs as a top-level statement, so evaluation flags work:
    "sum(r^k, k, 0, n-1), simpsum". `setup` runs first and may hold several
    statements: "load(simplify_sum)$ assume(m > 0)".

    Use ASCII names (lambda, not λ): Maxima passes Unicode straight through
    to TeX, where it may not typeset.
    """
    setup = setup.strip()
    if setup and not setup.endswith(("$", ";")):
        setup += "$"
    script = f'display2d: false$ {setup} {expr}$ print(concat("{_MARK}", tex1(%)))$'
    out = subprocess.run(
        [_executable(), "--very-quiet", f"--batch-string={script}"],
        capture_output=True, text=True, timeout=timeout,
    )
    # Maxima carries on after an error, leaving % as an earlier result, so an
    # error message anywhere means the marked line can't be trusted.
    if " -- an error." in out.stdout + out.stderr or _MARK not in out.stdout:
        raise MaximaError(f"Maxima failed on {expr!r}:\n{out.stdout}{out.stderr}")
    for line in out.stdout.splitlines():
        if line.startswith(_MARK):
            return line[len(_MARK):].strip()
    raise MaximaError(f"no result from Maxima for {expr!r}")


def maxima(expr, setup="", lhs=None, timeout=120):
    """Display the value of a Maxima expression, optionally as `lhs = value`.

    Returns an IPython Markdown object, which Jupyter and Quarto render as
    display maths.
    """
    from IPython.display import Markdown

    tex = maxima_tex(expr, setup, timeout)
    return Markdown(f"$$ {lhs + ' = ' if lhs else ''}{tex} $$")
