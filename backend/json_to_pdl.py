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

TRANSLATOR_VERSION = "0.2.0"

# --- reason codes: closed set (B.7) ----------------------------------------
# These are the "reasons" as to why the rule was passed to the queue for human amendment rather than being translated
MISSING_FIELD = "MISSING_FIELD" # Field with "MISSING_*". This means the record was incomplete
EMPTY_CONDITIONS = "EMPTY_CONDITIONS" # The record had no conditions. Nothing to translate
FORMULA_THRESHOLD = "FORMULA_THRESHOLD" # threshold_type in the JSON object was FORMULA. PDL's value rule only takes a constant, so it can't be expressed
MALFORMED_SHAPE = "MALFORMED_SHAPE" # the record's structure matches no shape the translator knows how to interpret
UNPARSEABLE_THRESHOLD = "UNPARSEABLE_THRESHOLD" # Claimed NUMERIC but the string isn't a single plain number (tolerance, range, time qualifier)
NEGATIVE_THRESHOLD = "NEGATIVE_THRESHOLD" # the number is negative, and the current grammar has no way to put a minus sign in the number position
UNMAPPED_VARIABLE = "UNMAPPED_VARIABLE" # the variable name isn't in variable_map.json and needs to be populated; the entry ships a suggested_pv so fixing it is one paste!

# --- direction -> operator (B.4): strict, never defaulted ------------------
OPERATOR = {"BELOW_MIN": "<", "ABOVE_MAX": ">"}

# --- lexer-derived shape rules (B.2) ----------------------------------------
# Process Value (PV) Rule from lexerRules.g4 for RegEx
# PV: ('A'..'Z') ('0'..'9' | 'a'..'z' | '.' )*;

# re.compile essentially converts the text-based rule (ex: "^[a-z0-9.]+$") into an object of your RegEx pattern so the rule doesn't have to be re-derived on every call!
LOCAL_NAME_RE = re.compile(r"^[a-z0-9.]+$") # Supplies the mandatory initial capital for variable_map.json---validates the "process" field
PROCESS_RE = re.compile(r"^[A-Z][0-9a-z]*$") # Validates that every value must be all lowercase/digits/dots (NO CAPS)


class MapValidationError(ValueError):
    """variable_map.json is unusable; abort the run (B.2)."""

class UnmappedVariable(KeyError):
    def __init__(self, variable: str):
        super().__init__(variable)
        self.variable = variable
        self.suggested = suggest_pv_name(variable)

class UnparseableThreshold(ValueError):
    pass

class NegativeThreshold(ValueError):
    pass

class AccountingError(RuntimeError):
    """translated + queued != records — a record vanished (B.0)."""

class _RecordError(Exception):
    """Internal: whole-record rejection into the review queue."""

    def __init__(self, reason: str, detail: str, suggested_pv: str | None = None,
                 unmapped_variable: str | None = None):
        super().__init__(detail)
        self.reason = reason
        self.detail = detail
        self.suggested_pv = suggested_pv
        self.unmapped_variable = unmapped_variable


# --- variable map (B.2) ------------------------------------------------------

def suggest_pv_name(variable: str) -> str:
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
    if d < 0:
        raise NegativeThreshold(verbatim or str(d))
    s = verbatim if verbatim is not None else format(d, "f")
    if s.startswith("."):
        s = "0" + s
    if "." not in s:
        s += "."
    return s


def normalize_threshold(raw: str) -> str:
    """parse + format; preserves the document's own digits when already plain."""
    d = parse_threshold(raw)
    cleaned = raw.strip().replace(",", "")
    if _PLAIN_RE.match(cleaned):
        return format_number(d, verbatim=cleaned.lstrip("+"))
    return format_number(d)


# --- provenance comments (B.6) -----------------------------------------------

def _sanitize_comment(text: str) -> str:
    """Untrusted OCR text goes into /* */ comments; '*/' would terminate the
    comment and inject tokens into the parse stream. Also folds newlines."""
    return re.sub(r"\s+", " ", str(text)).replace("*/", "* /").strip()


# --- record handling (B.3) -----------------------------------------------------

_CONDITION_FIELDS = ("direction", "threshold", "threshold_type", "units", "sub_variable")


def _record_as_dict(record) -> dict:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return record


def _find_missing_sentinel(rec: dict) -> str | None:
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
class ReportRow:
    """One row per input record. The review queue is the outcome == "queued"
    view of these rows — there is no second list to drift out of sync."""
    record_index: int
    function_name: str
    variable: str
    source_text: str
    outcome: str                        # "translated" | "queued"
    statements: list = field(default_factory=list)
    thresholds: list = field(default_factory=list)   # [{"raw": ..., "emitted": ...}]
    reason_code: str | None = None      # closed set (B.7); null when translated
    explanation: str | None = None      # human-readable; null when translated
    suggested_pv: str | None = None     # set only for UNMAPPED_VARIABLE
    unmapped_variable: str | None = None  # set only for UNMAPPED_VARIABLE: the exact name
                                          # that failed lookup — equals `variable` on the
                                          # value path, but may be a leg's sub_variable on
                                          # the conjunctive path; map fixes key on THIS


@dataclass
class TranslationResult:
    pdl_text: str
    report: list                        # one ReportRow per input record
    translated_count: int
    queued_count: int

    @property
    def queue(self):
        return [r for r in self.report if r.outcome == "queued"]


def _translate_condition(vmap: VariableMap, variable: str, cond: dict):
    """One condition leg -> (pv, operator, emitted-number). Any failure queues
    the whole record (atomicity, B.3)."""
    direction = cond.get("direction")
    op = OPERATOR.get(direction)
    if op is None:
        raise _RecordError(
            MALFORMED_SHAPE, f"NEEDS REVIEW: unrecognized direction {direction!r}"
        )
    try:
        pv = vmap.to_pv(variable)
    except UnmappedVariable as e:
        raise _RecordError(
            UNMAPPED_VARIABLE,
            f"NEEDS REVIEW: variable {e.variable!r} is not in variable_map.json",
            suggested_pv=e.suggested,
            unmapped_variable=e.variable,
        )
    raw = cond.get("threshold", "")
    try:
        emitted = normalize_threshold(raw)
    except UnparseableThreshold:
        raise _RecordError(
            UNPARSEABLE_THRESHOLD, f"NEEDS REVIEW: threshold {raw!r} is not a single plain number"
        )
    except NegativeThreshold:
        raise _RecordError(
            NEGATIVE_THRESHOLD,
            f"NEEDS REVIEW: threshold {raw!r} is negative; the grammar cannot represent it",
        )
    return pv, op, emitted


def _translate_record(rec: dict, vmap: VariableMap) -> tuple:
    """Returns ("value" | "match", comment, statements, thresholds)."""
    # B.3 classification, in spec order — reason codes must be stable.
    missing = _find_missing_sentinel(rec)
    if missing:
        raise _RecordError(MISSING_FIELD, f"NEEDS REVIEW: field {missing} carries a MISSING_ sentinel")

    conditions = rec.get("conditions") or []
    if not conditions:
        raise _RecordError(EMPTY_CONDITIONS, "NEEDS REVIEW: record has no conditions")

    for i, cond in enumerate(conditions):
        if cond.get("threshold_type") == "FORMULA":
            raise _RecordError(
                FORMULA_THRESHOLD,
                f"NEEDS REVIEW: conditions[{i}] threshold {cond.get('threshold')!r} is a FORMULA",
            )

    subs = [c.get("sub_variable") for c in conditions]
    named = [s is not None for s in subs]
    if any(named) and not all(named):
        raise _RecordError(
            MALFORMED_SHAPE, "NEEDS REVIEW: legs mix null and named sub_variable"
        )

    units = ", ".join(_sanitize_comment(c.get("units", "")) for c in conditions)
    comment = (
        f"/* {_sanitize_comment(rec.get('function_name', ''))} | {units} | "
        f"{_sanitize_comment(rec.get('source_text', ''))} */"
    )
    thresholds = []

    if not any(named):
        # value path: one statement per leg (simple == two-sided == N-sided)
        statements = []
        for cond in conditions:
            pv, op, num = _translate_condition(vmap, rec.get("variable", ""), cond)
            statements.append(f"value {pv} {op} {num};")
            thresholds.append({"raw": cond.get("threshold"), "emitted": num})
        return ("value", comment, statements, thresholds)

    # conjunctive path: one multipleMatch, one rn element per leg
    elements = []
    for cond in conditions:
        pv, op, num = _translate_condition(vmap, cond["sub_variable"], cond)
        elements.append(f"({pv} {op} {num})")
        thresholds.append({"raw": cond.get("threshold"), "emitted": num})
    statement = "multipleMatch " + " ".join(elements) + ";"
    return ("match", comment, [statement], thresholds)


def translate_records(records, vmap: VariableMap, doc_id: str = "unknown") -> TranslationResult:
    """Records in; PDL text + report out (queue is the queued view of the
    report). Pure function, no I/O."""
    value_blocks = []   # (comment, statements)
    match_blocks = []
    report = []

    for idx, raw_rec in enumerate(records):
        rec = _record_as_dict(raw_rec)
        row = dict(
            record_index=idx,
            function_name=rec.get("function_name", ""),
            variable=rec.get("variable", ""),
            source_text=rec.get("source_text", ""),
        )
        try:
            result = _translate_record(rec, vmap)
        except _RecordError as e:
            report.append(ReportRow(
                **row, outcome="queued",
                reason_code=e.reason, explanation=e.detail,
                suggested_pv=e.suggested_pv,
                unmapped_variable=e.unmapped_variable,
            ))
            continue
        if isinstance(result, tuple):
            kind, comment, statements, thresholds = result
            (value_blocks if kind == "value" else match_blocks).append((comment, statements))
            report.append(ReportRow(
                **row, outcome="translated",
                statements=list(statements), thresholds=thresholds,
            ))
        # anything else falls through uncounted — the invariant below catches it

    translated_count = len(value_blocks) + len(match_blocks)
    queued_count = sum(1 for r in report if r.outcome == "queued")
    if translated_count + queued_count != len(records):
        raise AccountingError(
            f"{len(records)} records in, {translated_count} translated + "
            f"{queued_count} queued out — a record was lost"
        )

    header = (
        f"/* generated by json_to_pdl v{TRANSLATOR_VERSION}\n"
        f"   document: {_sanitize_comment(doc_id)}\n"
        f"   records: {translated_count} translated / {queued_count} queued */"
    )
    lines = [header]
    # masterRule is an ordered sequence: every value before any multipleMatch (B.6)
    for comment, statements in value_blocks + match_blocks:
        lines.append("")
        lines.append(comment)
        lines.extend(statements)

    return TranslationResult(
        pdl_text="\n".join(lines) + "\n",
        report=report,
        translated_count=translated_count,
        queued_count=queued_count,
    )


# --- CLI: inspect I/O by hand (PDL -> stdout, report/queue -> stderr) ---------
# This is a visual test in the CLI
def _main(argv=None):
    import argparse
    import sys
    from dataclasses import asdict

    parser = argparse.ArgumentParser(
        description="Translate extract_rules JSON records to PDL monitoring needs."
    )
    parser.add_argument("records", help="JSON file containing an array of setpoint records")
    parser.add_argument(
        "--map",
        default=str(Path(__file__).parent / "important_files" / "variable_map.json"),
        help="variable_map.json path (default: important_files/variable_map.json)",
    )
    parser.add_argument("--doc-id", default=None, help="document id for the header (default: records filename)")
    parser.add_argument("--report", action="store_true", help="also print the full report + queue as JSON to stderr")
    args = parser.parse_args(argv)

    with open(args.records, encoding="utf-8") as f:
        records = json.load(f)
    vmap = VariableMap.load(args.map)
    result = translate_records(records, vmap, doc_id=args.doc_id or Path(args.records).stem)

    print(result.pdl_text, end="")  # stdout is pure PDL — pipeable/redirectable
    print(
        f"[json_to_pdl v{TRANSLATOR_VERSION}] {result.translated_count} translated, "
        f"{result.queued_count} queued",
        file=sys.stderr,
    )
    if args.report:
        # one row per record; the queue is the outcome == "queued" subset
        payload = {"report": [asdict(r) for r in result.report]}
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=sys.stderr)


if __name__ == "__main__":
    _main()
