import requests
import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import backend
import json_to_pdl

VMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "important_files", "variable_map.json")

if "vmap" not in st.session_state:
    st.session_state.vmap = json_to_pdl.VariableMap.load(VMAP_PATH) # Writes variable map to session state so that variables will persist streamlit runs

st.title("Auto Process Parser")
st.header("Please submit your document (PDF).")

uploaded_file = st.file_uploader("Upload", type="pdf") #Takes in a PDF uploaded by user
if uploaded_file is not None:
    st.success("File successfully uploaded!")

    # Streamlit reruns this whole script on every interaction, so only run MinerU + the two
    # Claude calls when this document hasn't been processed yet — reruns reuse session state
    if st.session_state.get("doc_name") != uploaded_file.name:
        file = {
            "files": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
        }

        data = { # MinerU settings. Check API docs @ http://127.0.0.1:8000/docs with MinerU backend running for more details. This is under POST /file_parse
            "lang_list": "ch",
            "backend": "pipeline", #You need a GPU for hybrid-engine. Use pipeline for CPU-only. CPU only is much cheaper, and we can achieve extremely similar results thanks to our LLM normalization!
            "effort": "medium",
            "parse_method": "auto",
            "formula_enable": "true",
            "image_analysis": "true",
            "return_md": "true",
            "return_middle_json": "false", # True if you need raw positioning blocks
            "return_images": "false"
        }

        try:
            with st.spinner("Parsing document... this may take a minute."): # Loading animation :D
                response = requests.post("http://127.0.0.1:8000/file_parse", files=file, data=data) # Post request to MinerU API. File gets passed to MinerU, along with settings for extraction.
            response.raise_for_status() # Check for HTTP error

            result = response.json() # Parses HTTP response body into a dict
            output = list(result["results"].values())[0] # Only one file uploaded, so grab the first (only) result
            markdown = output.get("md_content") # pulls md_content field from the output variable. If the field is missing, will return None

            if markdown: # If markdown is not None
                with st.spinner("Normalizing text..."):
                    normalized = backend.normalize_file(markdown)
                with st.spinner("Extracting rules..."):
                    extracted_rules = backend.extract_rules(normalized)

                st.session_state.records = extracted_rules
                st.session_state.doc_name = uploaded_file.name

        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")

    # Display + translation run from session state on every rerun — translate_records is
    # pure and instant (no LLM calls), so retranslating the full list each time is fine
    if st.session_state.get("doc_name") == uploaded_file.name:
        records = st.session_state.records
        st.success("Done!")

        if not records:
            st.warning("No extractable setpoints found in this document.")
        else:
            with st.expander("Extracted records (JSON)"):
                for record in records:
                    with st.expander(record.source_text):
                        st.code(record.model_dump_json(indent=2, exclude={"source_text"}), language="json")

        result = json_to_pdl.translate_records(records, st.session_state.vmap, doc_id=uploaded_file.name)

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
                with st.expander(f"{row.function_name} — {row.reason_code}"):
                    st.write(row.explanation)
                    st.caption(row.source_text)

            # Human-in-the-loop mapping panel: derived fresh from the queue every rerun, so it
            # always matches reality and dedupes variables shared by several queue rows
            unmapped = {r.variable: r.suggested_pv
                        for r in result.queue if r.reason_code == "UNMAPPED_VARIABLE"}

            if unmapped:
                with st.form("variable_map_form"):
                    st.subheader("Unmapped variables")
                    raw = {var: st.text_input(var, value=pv, key=f"pv_{var}")
                           for var, pv in unmapped.items()}
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
    
else:
    st.error("No file uploaded yet.")
