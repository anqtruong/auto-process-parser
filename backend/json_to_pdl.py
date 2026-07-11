"""Deterministic translator: extract_rules JSON records -> PDL monitoring needs.

Implements SECTION_B_SPEC.md (rationale in SECTION_B_RATIONALE.md).

Input:  list of setpoint_record (Pydantic models from important_files.json_schema)
        or their plain-dict equivalents (post-Gate-A edits).
Output: TranslationResult — PDL text conforming to MonitoringNeeds.g4, a review
        queue, and a per-record translation report, all from one pass.

Invariants (B.0):
- every record is translated or queued; imbalance raises AccountingError
- byte-identical output for identical input + map + TRANSLATOR_VERSION
- threshold digits are never changed except the two sanctioned rewrites:
  scientific-notation expansion and the integer trailing-dot suffix
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

TRANSLATOR_VERSION = "0.1.0"

# --- reason codes: closed set (B.7) ----------------------------------------
MISSING_FIELD = "MISSING_FIELD"
EMPTY_CONDITIONS = "EMPTY_CONDITIONS"
FORMULA_THRESHOLD = "FORMULA_THRESHOLD"
MALFORMED_SHAPE = "MALFORMED_SHAPE"
UNPARSEABLE_THRESHOLD = "UNPARSEABLE_THRESHOLD"
NEGATIVE_THRESHOLD = "NEGATIVE_THRESHOLD"
UNMAPPED_VARIABLE = "UNMAPPED_VARIABLE"

# --- direction -> operator (B.4): strict, never defaulted ------------------
OPERATOR = {"BELOW_MIN": "<", "ABOVE_MAX": ">"}

# --- lexer-derived shape rules (B.2) ----------------------------------------
LOCAL_NAME_RE = re.compile(r"^[a-z0-9.]+$")
PROCESS_RE = re.compile(r"^[A-Z][0-9a-z]*$")
PV_RE = re.compile(r"^[A-Z][0-9a-z.]*$")


class MapValidationError(ValueError):
    """variable_map.json is unusable; abort the run (B.2)."""


class UnmappedVariable(KeyError):
    def __init__(self, variable: str):
        super().__init__(variable)
        self.variable = variable
        self.suggested = mangle(variable)


class UnparseableThreshold(ValueError):
    pass


class NegativeThreshold(ValueError):
    pass


class AccountingError(RuntimeError):
    """translated + queued != records — a record vanished (B.0)."""


class _RecordError(Exception):
    """Internal: whole-record rejection into the review queue."""

    def __init__(self, reason: str, detail: str, suggested_pv: str | None = None):
        super().__init__(detail)
        self.reason = reason
        self.detail = detail
        self.suggested_pv = suggested_pv


# --- variable map (B.2) ------------------------------------------------------

def mangle(variable: str) -> str:
    """Propose a lexer-legal local name. Suggestion only — never emitted."""
    return re.sub(r"[^a-z0-9]", "", variable.lower())


@dataclass(frozen=True)
class VariableMap:
    process: str
    variables: dict

    @classmethod
    def from_dict(cls, data: dict) -> "VariableMap":
        process = data.get("process", "")
        variables = data.get("variables", {})
        if not PROCESS_RE.match(process or ""):
            raise MapValidationError(
                f"process {process!r} must match {PROCESS_RE.pattern}"
            )
        seen = {}
        for key, local in variables.items():
            if not isinstance(local, str) or not LOCAL_NAME_RE.match(local):
                raise MapValidationError(
                    f"local name {local!r} for {key!r} must match {LOCAL_NAME_RE.pattern}"
                )
            if not PV_RE.match(f"{process}.{local}"):
                raise MapValidationError(
                    f"assembled PV {process}.{local} is not a valid PV token"
                )
            if local in seen:
                raise MapValidationError(
                    f"PV collision: {seen[local]!r} and {key!r} both map to {local!r}"
                )
            seen[local] = key
        return cls(process=process, variables=dict(variables))

    @classmethod
    def load(cls, path) -> "VariableMap":
        with open(Path(path), encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_pv(self, variable: str) -> str:
        local = self.variables.get(variable.strip())
        if local is None:
            raise UnmappedVariable(variable.strip())
        return f"{self.process}.{local}"


# --- threshold normalization (B.5) -------------------------------------------

_SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
_PLAIN_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")
_SCI_RE = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*[×xX*]\s*10\^?([+-]?\d+)$")
_E_RE = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))[eE]([+-]?\d+)$")


def parse_threshold(raw: str) -> Decimal:
    """Layer 1 (policy-free): what number does this string denote?"""
    s = raw.strip().replace(",", "").translate(_SUPERSCRIPT)
    if _PLAIN_RE.match(s):
        return Decimal(s)
    m = _SCI_RE.match(s) or _E_RE.match(s)
    if m:
        return Decimal(m.group(1)).scaleb(int(m.group(2)))
    raise UnparseableThreshold(raw)


def format_number(d: Decimal, verbatim: str | None = None) -> str:
    """Layer 2 (THE DIEGO SEAM, B.5): spell a number so today's grammar
    accepts it. Current policy, pending the Section A grammar decision:

    - negative numbers are unrepresentable (no minus in the number position)
    - integers need a trailing dot (INT is declared before DOUBLE, so a bare
      integer lexes as INT and the `value` rule rejects it)
    - a bare leading dot needs a zero (DOUBLE requires a leading INT)

    `verbatim` carries the cleaned original spelling for digit preservation;
    None means the caller wants the Decimal rendered (sci-notation expansion).
    """
    if d < 0:
        raise NegativeThreshold(verbatim or str(d))
    s = verbatim if verbatim is not None else format(d, "f")
    if s.startswith("."):
        s = "0" + s
    if "." not in s:
        s += "."
    return s


def emit_threshold(raw: str) -> str:
    """parse + format; preserves the document's own digits when already plain."""
    d = parse_threshold(raw)
    cleaned = raw.strip().replace(",", "")
    if _PLAIN_RE.match(cleaned):
        return format_number(d, verbatim=cleaned.lstrip("+"))
    return format_number(d)


# --- provenance comments (B.6) -----------------------------------------------

def _sanitize(text: str) -> str:
    """Untrusted OCR text goes into /* */ comments; '*/' would terminate the
    comment and inject tokens into the parse stream. Also folds newlines."""
    return re.sub(r"\s+", " ", str(text)).replace("*/", "* /").strip()


# --- record handling (B.3) -----------------------------------------------------

_CONDITION_FIELDS = ("direction", "threshold", "threshold_type", "units", "sub_variable")


def _as_dict(record) -> dict:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return record


def _find_missing(rec: dict) -> str | None:
    def missing(v):
        return isinstance(v, str) and v.startswith("MISSING_")

    for key in ("variable", "function_name", "source_text"):
        if missing(rec.get(key)):
            return key
    for i, cond in enumerate(rec.get("conditions") or []):
        for key in _CONDITION_FIELDS:
            if missing(cond.get(key)):
                return f"conditions[{i}].{key}"
    return None


@dataclass
class _Translated:
    kind: str                      # "value" | "match"
    comment: str
    statements: list
    thresholds: list               # [{"raw": ..., "emitted": ...}]


@dataclass
class QueueEntry:
    record_index: int
    function_name: str
    variable: str
    reason: str
    detail: str
    suggested_pv: str | None
    source_text: str


@dataclass
class ReportRow:
    record_index: int
    function_name: str
    outcome: str                   # "translated" | "queued"
    statements: list = field(default_factory=list)
    thresholds: list = field(default_factory=list)
    reason: str | None = None
    detail: str | None = None


@dataclass
class TranslationResult:
    pdl_text: str
    queue: list
    report: list
    translated_count: int
    queued_count: int


def _leg(vmap: VariableMap, variable: str, cond: dict):
    """One condition leg -> (pv, operator, emitted-number). Any failure queues
    the whole record (atomicity, B.3)."""
    direction = cond.get("direction")
    op = OPERATOR.get(direction)
    if op is None:
        raise _RecordError(
            MALFORMED_SHAPE, f"unrecognized direction {direction!r}"
        )
    try:
        pv = vmap.to_pv(variable)
    except UnmappedVariable as e:
        raise _RecordError(
            UNMAPPED_VARIABLE,
            f"variable {e.variable!r} is not in variable_map.json",
            suggested_pv=e.suggested,
        )
    raw = cond.get("threshold", "")
    try:
        emitted = emit_threshold(raw)
    except UnparseableThreshold:
        raise _RecordError(
            UNPARSEABLE_THRESHOLD, f"threshold {raw!r} is not a single plain number"
        )
    except NegativeThreshold:
        raise _RecordError(
            NEGATIVE_THRESHOLD,
            f"threshold {raw!r} is negative; the grammar cannot represent it",
        )
    return pv, op, emitted


def _translate_record(rec: dict, vmap: VariableMap) -> _Translated:
    # B.3 classification, in spec order — reason codes must be stable.
    missing = _find_missing(rec)
    if missing:
        raise _RecordError(MISSING_FIELD, f"field {missing} carries a MISSING_ sentinel")

    conditions = rec.get("conditions") or []
    if not conditions:
        raise _RecordError(EMPTY_CONDITIONS, "record has no conditions")

    for i, cond in enumerate(conditions):
        if cond.get("threshold_type") == "FORMULA":
            raise _RecordError(
                FORMULA_THRESHOLD,
                f"conditions[{i}] threshold {cond.get('threshold')!r} is a FORMULA",
            )

    subs = [c.get("sub_variable") for c in conditions]
    named = [s is not None for s in subs]
    if any(named) and not all(named):
        raise _RecordError(
            MALFORMED_SHAPE, "legs mix null and named sub_variable"
        )

    units = ", ".join(_sanitize(c.get("units", "")) for c in conditions)
    comment = (
        f"/* {_sanitize(rec.get('function_name', ''))} | {units} | "
        f"{_sanitize(rec.get('source_text', ''))} */"
    )
    thresholds = []

    if not any(named):
        # value path: one statement per leg (simple == two-sided == N-sided)
        statements = []
        for cond in conditions:
            pv, op, num = _leg(vmap, rec.get("variable", ""), cond)
            statements.append(f"value {pv} {op} {num};")
            thresholds.append({"raw": cond.get("threshold"), "emitted": num})
        return _Translated("value", comment, statements, thresholds)

    # conjunctive path: one multipleMatch, one rn element per leg
    elements = []
    for cond in conditions:
        pv, op, num = _leg(vmap, cond["sub_variable"], cond)
        elements.append(f"({pv} {op} {num})")
        thresholds.append({"raw": cond.get("threshold"), "emitted": num})
    statement = "multipleMatch " + " ".join(elements) + ";"
    return _Translated("match", comment, [statement], thresholds)


def translate(records, vmap: VariableMap, doc_id: str = "unknown") -> TranslationResult:
    """Records in; PDL text + queue + report out. Pure function, no I/O."""
    value_blocks = []   # (comment, statements)
    match_blocks = []
    queue = []
    report = []

    for idx, raw_rec in enumerate(records):
        rec = _as_dict(raw_rec)
        fn = rec.get("function_name", "")
        try:
            result = _translate_record(rec, vmap)
        except _RecordError as e:
            entry = QueueEntry(
                record_index=idx,
                function_name=fn,
                variable=rec.get("variable", ""),
                reason=e.reason,
                detail=e.detail,
                suggested_pv=e.suggested_pv,
                source_text=rec.get("source_text", ""),
            )
            queue.append(entry)
            report.append(ReportRow(
                record_index=idx, function_name=fn, outcome="queued",
                reason=e.reason, detail=e.detail,
            ))
            continue
        if isinstance(result, _Translated):
            block = (result.comment, result.statements)
            (value_blocks if result.kind == "value" else match_blocks).append(block)
            report.append(ReportRow(
                record_index=idx, function_name=fn, outcome="translated",
                statements=list(result.statements), thresholds=result.thresholds,
            ))
        # anything else falls through uncounted — the invariant below catches it

    translated_count = len(value_blocks) + len(match_blocks)
    if translated_count + len(queue) != len(records):
        raise AccountingError(
            f"{len(records)} records in, {translated_count} translated + "
            f"{len(queue)} queued out — a record was lost"
        )

    header = (
        f"/* generated by json_to_pdl v{TRANSLATOR_VERSION}\n"
        f"   document: {_sanitize(doc_id)}\n"
        f"   records: {translated_count} translated / {len(queue)} queued */"
    )
    lines = [header]
    # masterRule is an ordered sequence: every value before any multipleMatch (B.6)
    for comment, statements in value_blocks + match_blocks:
        lines.append("")
        lines.append(comment)
        lines.extend(statements)

    return TranslationResult(
        pdl_text="\n".join(lines) + "\n",
        queue=queue,
        report=report,
        translated_count=translated_count,
        queued_count=len(queue),
    )
