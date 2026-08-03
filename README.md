# HEAD-END Ingestion Pipeline for the SCADA Compiler

Streamlines the translation process from process document -> rules and setpoints -> Process Description Language for plants.

## Pipeline Overview

```mermaid
flowchart LR
    A([PDF Upload]) -->|HTTP POST| B[MinerU API\nlocal server]
    B -->|Markdown| C[Claude Haiku\nNormalization]
    C -->|Normalized text| D[Claude Sonnet\nRule Extraction]
    D -->|Structured JSON| E([User Review\nStreamlit Frontend])
```

## Tech Stack

**Frontend:**
- Streamlit

**Backend:**
- MinerU (PDF parsing / OCR)
- Claude API (text normalization + rule extraction)
- Pydantic (output schema validation)

## Prerequisites

Create a `.env` file in the `backend/` directory with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_key_here
```

## How to Use

**1. Start the MinerU backend**

```bash
cd backend
source .venv/bin/activate
mineru-api --host 0.0.0.0 --port 8000
```

**2. Start the Streamlit frontend (make sure the venv from step 1 is activated)**

```bash
cd frontend
streamlit run frontend.py
```

## Useful Links

- [MinerU API docs](http://127.0.0.1:8000/docs#/) — **Must have MinerU local server running (step 1)**