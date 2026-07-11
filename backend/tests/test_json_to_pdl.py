"""Section B tests (SECTION_B_SPEC.md B.8).

Golden tests are the eight worked examples from the extract_rules system
prompt in backend.py — the canonical extractor input/output pairs.
"""

import pytest

import json_to_pdl as j2p
from json_to_pdl import (
    AccountingError,
    MapValidationError,
    VariableMap,
    emit_threshold,
    mangle,
    parse_threshold,
    translate,
)

VMAP = VariableMap.from_dict({
    "process": "P1",
    "variables": {
        "Coolant Header Pressure": "coolantheaderpressure",
        "Turbine Casing Pressure": "turbinecasingpressure",
        "Surge Tank Level": "surgetanklevel",
        "Vessel Coolant Level": "vesselcoolantlevel",
        "Vent Stack Radiation": "ventstackradiation",
        "Steam Flow": "steamflow",
        "Drum Level": "drumlevel",
    },
})


def rec(variable, function_name, conditions, source_text="| row |"):
    return {
        "variable": variable,
        "function_name": function_name,
        "source_text": source_text,
        "conditions": conditions,
    }


def cond(direction, threshold, threshold_type="NUMERIC", units="psig", sub_variable=None):
    return {
        "direction": direction,
        "threshold": threshold,
        "threshold_type": threshold_type,
        "units": units,
        "sub_variable": sub_variable,
    }


# --- golden tests: prompt examples 1-8 --------------------------------------

def test_example_1_lower_bound(assert_parses):
    records = [rec("Coolant Header Pressure", "Coolant Header Pressure - Low",
                   [cond("BELOW_MIN", "1420")])]
    result = translate(records, VMAP)
    assert "value P1.coolantheaderpressure < 1420.;" in result.pdl_text
    assert result.translated_count == 1 and result.queued_count == 0
    assert_parses(result.pdl_text)


def test_example_2_upper_bound(assert_parses):
    records = [rec("Turbine Casing Pressure", "Turbine Casing Pressure - High",
                   [cond("ABOVE_MAX", "92.4", units="psia")])]
    result = translate(records, VMAP)
    assert "value P1.turbinecasingpressure > 92.4;" in result.pdl_text
    assert_parses(result.pdl_text)


def test_example_3_two_sided(assert_parses):
    records = [rec("Surge Tank Level", "Surge Tank Level", [
        cond("BELOW_MIN", "30.2", units="in. H₂O"),
        cond("ABOVE_MAX", "74.8", units="in. H₂O"),
    ])]
    result = translate(records, VMAP)
    low = result.pdl_text.index("value P1.surgetanklevel < 30.2;")
    high = result.pdl_text.index("value P1.surgetanklevel > 74.8;")
    assert low < high
    assert result.translated_count == 1  # one record, two statements
    assert len(result.report[0].statements) == 2
    assert_parses(result.pdl_text)


def test_example_4_formula_queued():
    records = [rec("Feed Header Pressure", "Feed Header Pressure - Low",
                   [cond("BELOW_MIN", "7.44 × T_loop − 2210",
                         threshold_type="FORMULA", units="psig (T_loop in °F)")])]
    result = translate(records, VMAP)
    assert result.translated_count == 0 and result.queued_count == 1
    assert result.queue[0].reason == j2p.FORMULA_THRESHOLD


def test_example_5_conjunctive(assert_parses):
    records = [rec("Feed/Steam Flow Mismatch coincident with Low Drum Level",
                   "Feed/Steam Flow Mismatch coincident with Low Drum Level", [
        cond("ABOVE_MAX", "38.0", units="% of full flow", sub_variable="Steam Flow"),
        cond("BELOW_MIN", "22", units="% of span", sub_variable="Drum Level"),
    ])]
    result = translate(records, VMAP)
    assert "multipleMatch (P1.steamflow > 38.0) (P1.drumlevel < 22.);" in result.pdl_text
    assert_parses(result.pdl_text)


def test_example_6_distinct_trip_levels(assert_parses):
    records = [
        rec("Vessel Coolant Level", "Vessel Coolant Level - Low",
            [cond("BELOW_MIN", "88.4", units="in.")]),
        rec("Vessel Coolant Level", "Vessel Coolant Level - Low-Low",
            [cond("BELOW_MIN", "40.1", units="in.")]),
    ]
    result = translate(records, VMAP)
    assert "value P1.vesselcoolantlevel < 88.4;" in result.pdl_text
    assert "value P1.vesselcoolantlevel < 40.1;" in result.pdl_text
    assert result.translated_count == 2
    assert_parses(result.pdl_text)


def test_example_7_scientific_notation(assert_parses):
    records = [rec("Vent Stack Radiation", "Vent Stack Radiation - High",
                   [cond("ABOVE_MAX", "4.7×10⁻³", units="μCi/cc")])]
    result = translate(records, VMAP)
    assert "value P1.ventstackradiation > 0.0047;" in result.pdl_text
    assert result.report[0].thresholds == [{"raw": "4.7×10⁻³", "emitted": "0.0047"}]
    assert_parses(result.pdl_text)


def test_example_8_empty_input(assert_parses):
    result = translate([], VMAP, doc_id="empty-doc")
    assert result.translated_count == 0 and result.queued_count == 0
    assert "0 translated / 0 queued" in result.pdl_text
    assert "value" not in result.pdl_text
    assert_parses(result.pdl_text)  # header-only file must still parse


# --- threshold normalization (B.5) -------------------------------------------

def test_thousands_commas():
    assert emit_threshold("1,941") == "1941."


def test_precision_preserved():
    assert emit_threshold("38.0") == "38.0"
    assert emit_threshold("619.08") == "619.08"


def test_integer_trailing_dot():
    assert emit_threshold("1420") == "1420."


def test_leading_dot_gets_zero():
    assert emit_threshold(".5") == "0.5"


def test_ascii_scientific():
    assert emit_threshold("4.7e-3") == "0.0047"
    assert emit_threshold("1.0×10⁻²") == "0.010"


def test_unparseable_threshold_queues():
    records = [rec("Steam Flow", "f", [cond("BELOW_MIN", "3558 volts for 10 ± 1.5 sec")])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.UNPARSEABLE_THRESHOLD


def test_negative_threshold_queues():
    records = [rec("Steam Flow", "f", [cond("BELOW_MIN", "-10")])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.NEGATIVE_THRESHOLD


def test_parse_threshold_rejects_junk():
    for junk in ("", "N.A.", "≥ 1420", "10 to 20", "1.2.3"):
        with pytest.raises(j2p.UnparseableThreshold):
            parse_threshold(junk)


# --- classification and shape policy (B.3, B.4) -------------------------------

def test_missing_sentinel_queues():
    records = [rec("Steam Flow", "f", [cond("BELOW_MIN", "10", units="MISSING_UNITS")])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.MISSING_FIELD
    assert "conditions[0].units" in result.queue[0].detail


def test_empty_conditions_queue():
    records = [rec("Steam Flow", "f", [])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.EMPTY_CONDITIONS


def test_mixed_legs_queue():
    records = [rec("Steam Flow", "f", [
        cond("BELOW_MIN", "10"),
        cond("ABOVE_MAX", "20", sub_variable="Drum Level"),
    ])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.MALFORMED_SHAPE


def test_invalid_direction_queues():
    # Gate A hands back edited dicts that bypass Pydantic's enum
    records = [rec("Steam Flow", "f", [cond("BELOW", "10")])]
    result = translate(records, VMAP)
    assert result.queue[0].reason == j2p.MALFORMED_SHAPE


def test_three_leg_conjunctive(assert_parses):
    records = [rec("Summary", "f", [
        cond("ABOVE_MAX", "1.", sub_variable="Steam Flow"),
        cond("BELOW_MIN", "2.", sub_variable="Drum Level"),
        cond("ABOVE_MAX", "3.", sub_variable="Vent Stack Radiation"),
    ])]
    result = translate(records, VMAP)
    statement = result.report[0].statements[0]
    assert statement.count("(") == 3
    assert_parses(result.pdl_text)


def test_unmapped_variable_suggests_pv():
    records = [rec("Reactor Building Spray Flow", "f", [cond("BELOW_MIN", "10")])]
    result = translate(records, VMAP)
    entry = result.queue[0]
    assert entry.reason == j2p.UNMAPPED_VARIABLE
    assert entry.suggested_pv == "reactorbuildingsprayflow"


# --- variable map validation (B.2) --------------------------------------------

def test_map_collision_rejected():
    with pytest.raises(MapValidationError, match="collision"):
        VariableMap.from_dict({
            "process": "P1",
            "variables": {"Steam Flow": "steamflow", "Steam  Flow (B)": "steamflow"},
        })


def test_map_bad_local_name_rejected():
    with pytest.raises(MapValidationError):
        VariableMap.from_dict({"process": "P1", "variables": {"X": "Bad_Name"}})


def test_map_bad_process_rejected():
    with pytest.raises(MapValidationError):
        VariableMap.from_dict({"process": "p1", "variables": {}})


def test_mangle():
    assert mangle("Feed/Steam Flow Mismatch") == "feedsteamflowmismatch"
    assert mangle("Vessel Coolant Level - Low-Low") == "vesselcoolantlevellowlow"


# --- emission, ordering, sanitization (B.6) -------------------------------------

def test_values_precede_multiplematch_when_interleaved(assert_parses):
    records = [
        rec("Steam Flow", "v1", [cond("BELOW_MIN", "1.")]),
        rec("Summary", "m1", [
            cond("ABOVE_MAX", "2.", sub_variable="Drum Level"),
            cond("BELOW_MIN", "3.", sub_variable="Steam Flow"),
        ]),
        rec("Drum Level", "v2", [cond("ABOVE_MAX", "4.")]),
    ]
    result = translate(records, VMAP)
    text = result.pdl_text
    assert text.rindex("value ") < text.index("multipleMatch ")
    assert_parses(result.pdl_text)


def test_comment_injection_sanitized(assert_parses):
    records = [rec("Steam Flow", "f",
                   [cond("BELOW_MIN", "10")],
                   source_text="| garbled */ value P1.x < 1.; /* row |")]
    result = translate(records, VMAP)
    assert "*/ value" not in result.pdl_text
    assert result.translated_count == 1
    assert_parses(result.pdl_text)  # injected tokens would fail the parse


def test_provenance_comment_present():
    records = [rec("Steam Flow", "Steam Flow - Low", [cond("BELOW_MIN", "10")],
                   source_text="| Steam Flow - Low | ≥ 10 | psig |")]
    result = translate(records, VMAP)
    assert "/* Steam Flow - Low | psig | | Steam Flow - Low | ≥ 10 | psig | */" in result.pdl_text


def test_header_contains_version_doc_and_counts():
    records = [rec("Steam Flow", "f", [cond("BELOW_MIN", "10")])]
    result = translate(records, VMAP, doc_id="ML17056A228_p3")
    assert f"json_to_pdl v{j2p.TRANSLATOR_VERSION}" in result.pdl_text
    assert "document: ML17056A228_p3" in result.pdl_text
    assert "records: 1 translated / 0 queued" in result.pdl_text


# --- invariants (B.0) ------------------------------------------------------------

def test_determinism_byte_identical():
    records = [
        rec("Steam Flow", "f1", [cond("BELOW_MIN", "10")]),
        rec("Unmapped Thing", "f2", [cond("ABOVE_MAX", "20")]),
    ]
    a = translate(records, VMAP, doc_id="d")
    b = translate(records, VMAP, doc_id="d")
    assert a.pdl_text == b.pdl_text


def test_accounting_covers_every_record():
    records = [
        rec("Steam Flow", "ok", [cond("BELOW_MIN", "10")]),
        rec("Nope", "queued", [cond("ABOVE_MAX", "20")]),
    ]
    result = translate(records, VMAP)
    assert result.translated_count + result.queued_count == len(records)
    assert {row.record_index for row in result.report} == {0, 1}


def test_accounting_error_on_lost_record(monkeypatch):
    # simulate the "forgot a code path" bug class: a result translate() does
    # not recognize falls through uncounted, and the invariant must catch it
    monkeypatch.setattr(j2p, "_translate_record", lambda rec, vmap: object())
    with pytest.raises(AccountingError):
        translate([rec("Steam Flow", "f", [cond("BELOW_MIN", "10")])], VMAP)
