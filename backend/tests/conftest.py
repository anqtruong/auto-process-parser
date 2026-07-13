"""Test wiring for Section B.

Puts backend/ and the generated ANTLR Python target on sys.path, and provides
assert_parses (B.9): a parse check that HARD-FAILS on any syntax error —
ANTLR's default strategy recovers and continues, which would let garbage pass.

Regenerate the parser target with:
    cd backend/ANTLR/monitoringNeeds
    antlr -Dlanguage=Python3 -o ../../tests/parsing MonitoringNeeds.g4
"""

import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent
PARSING = BACKEND / "tests" / "parsing"
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(PARSING))

_PARSER_AVAILABLE = (PARSING / "MonitoringNeedsParser.py").exists()


def _assert_parses(pdl_text: str) -> None:
    from antlr4 import CommonTokenStream, InputStream, Token
    from antlr4.error.ErrorListener import ErrorListener

    from MonitoringNeedsLexer import MonitoringNeedsLexer
    from MonitoringNeedsParser import MonitoringNeedsParser

    class Raising(ErrorListener):
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            raise SyntaxError(f"PDL parse error line {line}:{column} {msg}")

    lexer = MonitoringNeedsLexer(InputStream(pdl_text))
    lexer.removeErrorListeners()
    lexer.addErrorListener(Raising())
    tokens = CommonTokenStream(lexer)
    parser = MonitoringNeedsParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(Raising())
    parser.masterRule()
    # masterRule has no EOF anchor; trailing garbage would be silently ignored
    if tokens.LA(1) != Token.EOF:
        raise SyntaxError(
            f"PDL not fully consumed; stopped before {tokens.LT(1).text!r}"
        )


@pytest.fixture
def assert_parses():
    if not _PARSER_AVAILABLE:
        pytest.skip("generated ANTLR Python target missing (see conftest header)")
    return _assert_parses
