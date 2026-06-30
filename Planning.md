
Streamlit Frontend must:

(1) take in the PDF.
(2) technically we can just say that they have to submit specific pages. So we'll start with that, but eventually maybe we'd like to make it so they can select specific pages in-app.

(1) Extract the text from the document, we must pass the .md to the LLM to normalize the information 
    - How do we do this?
        Claude files API! - https://platform.claude.com/docs/en/build-with-claude/files
        (1a) Claude receives the .md via files API
        (1b) Claude amends the .md via Claude Messages API
        (1c) Claude returns the .md (figuring out)
(2) We should have the user validate it against the pdf to make sure the output is correct.
    - What does this entail?
        - Perhaps a side-by-side UI to compare the original pdf against the .md.
        - Allow user to manually edit, save, then approve
(3) Pass the validated .md to LLM to translate into PDL
    - How?
        (3a) Claude receives the .md via Files API
        (3b) Claude amends the .md via Claude Messages API



in frontend:
streamlit run frontend.py

in backend:

source .venv/bin/activate
mineru-api --host 0.0.0.0 --port 8000
http://127.0.0.1:8000/docs#/ for documentation