import requests
import streamlit as st

st.title("Auto Process Parser by An Truong")
st.header("")
st.header("Please submit your document (PDF).")

uploadedFile = st.file_uploader("Upload", type="pdf") #Takes in a PDF uploaded by user
if uploadedFile is not None:
    st.success("File successfully uploaded!")
else:
    st.error("File was not successfully uploaded, please try again.")
