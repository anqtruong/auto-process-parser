import requests
import streamlit as st
import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import backend

st.title("Auto Process Parser")
st.header("Please submit your document (PDF).")

uploaded_file = st.file_uploader("Upload", type="pdf") #Takes in a PDF uploaded by user
if uploaded_file is not None:
    st.success("File successfully uploaded!")

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

            st.success("Done!")

            if not extracted_rules:
                st.warning("No extractable setpoints found in this document.")
            else:
                for record in extracted_rules:
                    st.write(record.source_text)
                    st.code(record.model_dump_json(indent=2, exclude={"source_text"}), language="json")

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")

else:
    st.error("No file uploaded yet.")
