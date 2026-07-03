import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from json_schema import setpoint_record, condition, direction, threshold_type

# Frontend tester (no API calls)

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
st.header("Please submit your document (PDF).")
st.info("Using hardcoded test data. No API calls made.")

uploaded_file = st.file_uploader("Upload", type="pdf") 
if uploaded_file is not None:
    st.success("File successfully uploaded!")

if not extracted_rules:
    st.warning("No extractable setpoints found in this document.")
else:


    """
     for record in extracted_rules:
        with st.expander(record.source_text):
            st.text_area(record.model_dump_json(indent=2, exclude={"source_text"}), language
    """


    """for i, record in enumerate(extracted_rules):
        with st.expander(record.source_text):
            edited = st.text_area(
                "Edit JSON",
                value=record.model_dump_json(indent=2, exclude={"source_text"}),
                height=200,
                key=f"editor_{i}",
            )
            if st.button("Validate", key=f"validate_{i}"):
                try:
                    import json
                    parsed = json.loads(edited)
                    st.success("Valid JSON")
                    st.json(parsed)
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {e}")
"""