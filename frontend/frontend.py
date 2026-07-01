import requests
import streamlit as st
import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
import backend

st.title("Auto Process Parser by An Truong")
st.header("Please submit your document (PDF).")

uploadedFile = st.file_uploader("Upload", type="pdf") #Takes in a PDF uploaded by user
if uploadedFile is not None:
    st.success("File successfully uploaded!")

    file = {
        "files": (uploadedFile.name, uploadedFile.getvalue(), "application/pdf")
    }

    data = {
        "lang_list": "ch",
        "backend": "pipeline", #You need a GPU for hybrid-engine. Use use ipeline for CPU.
        "effort": "medium",
        "parse_method": "auto",
        "formula_enable": "true",
        "image_analysis": "true",
        "return_md": "true",
        "return_middle_json": "false", # True if you need raw positioning blocks
        "return_images": "false" 
    }

    try:
        with st.spinner("Parsing document... this may take a minute."):
            response = requests.post("http://127.0.0.1:8000/file_parse", files=file, data=data)
        response.raise_for_status()

        result = response.json()
        output = list(result["results"].values())[0]
        markdown = output.get("md_content")

        if markdown:
            st.success("Done!")
            st.markdown(backend.normalizeFile(markdown))

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")

else:
    st.error("No file uploaded yet.")
