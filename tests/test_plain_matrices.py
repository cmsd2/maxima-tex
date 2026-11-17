"""Matrix rewriting, on synthetic tex() output, so these run without Maxima."""

from maxima_tex import _plain_matrices

BEGIN = r"\ifx\endpmatrix\undefined\pmatrix{\else\begin{pmatrix}\fi"
END = r"\ifx\endpmatrix\undefined}\else\end{pmatrix}\fi"


def test_two_by_two():
    tex = BEGIN + r" a&b\cr c&d\cr " + END
    assert _plain_matrices(tex) == r"\begin{pmatrix} a&b \\ c&d \end{pmatrix}"


def test_column_vector_in_an_expression():
    tex = r"\left[ " + BEGIN + r" 1\cr x^2\cr " + END + r"  , 3 \right]"
    assert _plain_matrices(tex) == (
        r"\left[ \begin{pmatrix} 1 \\ x^2 \end{pmatrix}  , 3 \right]"
    )


def test_nested_matrices():
    tex = BEGIN + " " + BEGIN + r" 1\cr " + END + r" \cr " + END
    assert _plain_matrices(tex) == (
        r"\begin{pmatrix} \begin{pmatrix} 1 \end{pmatrix}  \end{pmatrix}"
    )


def test_empty_matrix():
    assert _plain_matrices(BEGIN + " " + END) == r"\begin{pmatrix} \end{pmatrix}"


def test_leaves_other_tex_alone():
    for tex in [r"{{1}\over{\lambda}}", r"\cr a", r"\mbox{ \crash }", ""]:
        assert _plain_matrices(tex) == tex
    # \crash inside a matrix is a different control word, not a row end.
    assert _plain_matrices(BEGIN + r" \crash\cr " + END) == (
        r"\begin{pmatrix} \crash \end{pmatrix}"
    )
