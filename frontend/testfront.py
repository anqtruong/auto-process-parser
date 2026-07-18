import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import json_to_pdl
from important_files.json_schema import setpoint_record, condition, direction, threshold_type
from pydantic import ValidationError

# Frontend tester (no API calls) — skips MinerU + Claude by using hardcoded records.
# UI iteration happens HERE first; frontend.py's display block gets synced from this
# file once the UI is approved (identical through commit 096b4f6).

VMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "important_files", "variable_map.json")

if "vmap" not in st.session_state:
    st.session_state.vmap = json_to_pdl.VariableMap.load(VMAP_PATH) # Writes variable map to session state so that variables will persist streamlit runs

# --- Testbed data ---
extracted_rules = [
    setpoint_record(
        variable="RC High Pressure",
        function_name="rc_high_pressure_trip",
        source_text="RC High Pressure: Trip if pressure exceeds 2200 psia.",
        conditions=[
            condition(
                direction=direction.ABOVE_MAX,
                threshold="2200",
                threshold_type=threshold_type.NUMERIC,
                units="psia",
                sub_variable=None,
            )
        ],
    ),
    setpoint_record(
        variable="Water Tank Low Level",
        function_name="water_tank_low_level_alarm",
        source_text="Water Tank Low Level: Alarm when level drops below 10% of capacity.",
        conditions=[
            condition(
                direction=direction.BELOW_MIN,
                threshold="0.10 * capacity",
                threshold_type=threshold_type.FORMULA,
                units="%",
                sub_variable=None,
            )
        ],
    ),
    setpoint_record(
        variable="Coolant Outlet Temp",
        function_name="coolant_outlet_temp_trip",
        source_text="Coolant Outlet Temp: Trip if outlet temperature exceeds 325°C or inlet flow drops below 50 kg/s.",
        conditions=[
            condition(
                direction=direction.ABOVE_MAX,
                threshold="325",
                threshold_type=threshold_type.NUMERIC,
                units="°C",
                sub_variable=None,
            ),
            condition(
                direction=direction.BELOW_MIN,
                threshold="50",
                threshold_type=threshold_type.NUMERIC,
                units="kg/s",
                sub_variable="Coolant Inlet Flow",
            ),
        ],
    ),
]

# --- Display (mirrors frontend.py) ---
st.title("Auto Process Parser — Frontend Testbed")
st.info("Using hardcoded test data. No API calls made.")

if "records" not in st.session_state:
    st.session_state.records = extracted_rules # session copy: amendments must survive reruns
records = st.session_state.records

if not records:
    st.warning("No extractable setpoints found in this document.")
else:
    with st.expander("Extracted records (JSON)"):
        for record in records:
            with st.expander(record.source_text):
                st.code(record.model_dump_json(indent=2, exclude={"source_text"}), language="json")

result = json_to_pdl.translate_records(records, st.session_state.vmap, doc_id="testbed")

left, right = st.columns(2, border=True)

with left:
    st.subheader(f"Translated ({result.translated_count})")
    for row in result.report:
        if row.outcome == "translated":
            with st.expander(row.function_name):
                st.code("\n".join(row.statements))
                st.caption(row.source_text)

with right:
    st.subheader(f"Queued ({result.queued_count})")
    for row in result.queue:
        if row.reason_code == json_to_pdl.UNMAPPED_VARIABLE:
            continue # these rows are represented by the mapping panel below — showing them here too duplicates, and amending the record can't fix a map problem
        with st.expander(f"{row.function_name} — {row.reason_code}"):
            st.write(row.explanation)
            st.caption(row.source_text)
            if row.reason_code == json_to_pdl.FORMULA_THRESHOLD:
                st.caption("REASON: Formula thresholds can't translate until the grammar "
                           "supports them.")
            with st.form(f"amend_form_{row.record_index}"):
                edited = st.text_area(
                    "Amend record JSON",
                    value=records[row.record_index].model_dump_json(indent=2),
                    height=240,
                    key=f"amend_{row.record_index}",
                )
                if st.form_submit_button("Apply amendment"):
                    try:
                        # schema-validate BEFORE storing: a non-conforming record in session
                        # state would crash translate_records on every rerun (bricked session)
                        st.session_state.records[row.record_index] = setpoint_record.model_validate_json(edited)
                        st.rerun() # translation above already ran with the old record this pass
                    except ValidationError as e:
                        st.error(str(e)) # no rerun: error stays visible, text stays editable

    # Human-in-the-loop mapping panel: derived fresh from the queue every rerun, so it
    # always matches reality and dedupes variables shared by several queue rows
    unmapped = {}
    for r in result.queue:
        if r.reason_code == json_to_pdl.UNMAPPED_VARIABLE:
            entry = unmapped.setdefault(r.unmapped_variable, {"pv": r.suggested_pv, "fns": []}) # key on the name that actually failed lookup — on conjunctive records r.variable is the summary name, not the unmapped leg
            entry["fns"].append(r.function_name)

    if unmapped:
        with st.form("variable_map_form"):
            st.subheader("Unmapped variables")
            raw = {}
            for var, entry in unmapped.items():
                raw[var] = st.text_input(var, value=entry["pv"], key=f"pv_{var}")
                st.caption("referenced by: " + ", ".join(entry["fns"]))
            submitted = st.form_submit_button("Apply mappings")
        if submitted:
            edits = {var: name.strip() for var, name in raw.items() if name.strip()} # blank = skip: user can map a subset, the rest stay queued
            if edits:
                try:
                    # rebuild via from_dict so existing validation (name format + PV collisions) runs; never mutate in place
                    st.session_state.vmap = json_to_pdl.VariableMap.from_dict({
                        "process": st.session_state.vmap.process,
                        "variables": {**st.session_state.vmap.variables, **edits},
                    })
                    st.rerun() # translation above already ran with the old map this pass — restart so no stale frame renders
                except json_to_pdl.MapValidationError as e:
                    st.error(str(e)) # no rerun: keep the error visible and the inputs intact

st.code(result.pdl_text)
