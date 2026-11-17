import shutil
import os

import pytest

from maxima_tex import MaximaError, maxima, maxima_tex

pytestmark = pytest.mark.skipif(
    not (os.environ.get("MAXIMA") or shutil.which("maxima")),
    reason="Maxima is not installed",
)


def test_integral():
    assert maxima_tex("integrate(x*exp(-x), x, 0, inf)") == "1"


def test_setup_runs_first():
    tex = maxima_tex(
        "simplify_sum(sum(k*exp(-m)*m^k/k!, k, 0, inf))", setup="load(simplify_sum)"
    )
    assert tex == "m"


def test_assumptions_in_setup():
    tex = maxima_tex("integrate(x*lambda*exp(-lambda*x), x, 0, inf)",
                     setup="assume(lambda > 0)")
    assert tex == r"{{1}\over{\lambda}}"


def test_carets_and_quotes_survive_the_command_line():
    # On Windows maxima is a .bat file, so cmd.exe sits between us and Maxima.
    assert maxima_tex('concat("a", "b")') == r"\mbox{ ab }"
    assert maxima_tex("sum(r^k, k, 0, n-1), simpsum") == r"{{r^{n}-1}\over{r-1}}"


def test_errors_raise_rather_than_return_a_stale_value():
    with pytest.raises(MaximaError, match="Maxima failed"):
        maxima_tex("x % 3")


def test_matrix_is_a_plain_pmatrix():
    # MathJax can't read the \ifx wrapper Maxima puts round matrices.
    assert maxima_tex("matrix([1,2],[3,4])") == (
        r"\begin{pmatrix} 1&2 \\ 3&4 \end{pmatrix}"
    )
    assert maxima_tex("ident(2) . x") == (
        r"\begin{pmatrix} 1&0 \\ 0&1 \end{pmatrix} \cdot x"
    )


def test_display_wraps_in_display_maths():
    pytest.importorskip("IPython")
    assert maxima("1+1", lhs="y").data == "$$ y = 2 $$"
    assert maxima("1+1").data == "$$ 2 $$"


def test_missing_executable_is_reported(monkeypatch):
    monkeypatch.setenv("MAXIMA", "")
    monkeypatch.setenv("PATH", "")
    with pytest.raises(MaximaError, match="not on PATH"):
        maxima_tex("1")
