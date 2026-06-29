import requests
import streamlit as st

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
        "backend": "hybrid-engine",
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
            st.markdown(markdown)

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")

else:
    st.error("No file uploaded yet.")

#Test MinerU API connection
"""try:
    response = requests.get("http://127.0.0.1:8000/health")
    st.write(response.json())

except requests.exceptions.ConnectionError:
    st.error("Backend couldn't be reached")"""