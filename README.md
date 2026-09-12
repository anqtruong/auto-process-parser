# HEAD-END Ingestion Pipeline for the SCADA Compiler

Streamlines the translation process from process document -> rules and setpoints -> Process Description Language for plants.

## Pipeline Overview

<img width="1097" height="221" alt="image" src="https://github.com/user-attachments/assets/4b0e50fa-c9a0-4a96-abc5-6cbed57fd230" />

## Pipeline Architecture
<img width="1103" height="619" alt="image" src="https://github.com/user-attachments/assets/52156456-6f3c-4ba8-9dbf-f851d65a10d6" />


## Tech Stack

**Frontend:**
- Streamlit
- requests (calls the MinerU API)

**Backend:**
- MinerU (PDF parsing / OCR)
- Claude API (text normalization + rule extraction)
- Pydantic (extraction schema validation)
- python-dotenv (API-key loading)
- Deterministic PDL translator (`json_to_pdl.py`) — emits PDL conforming to the ANTLR `MonitoringNeeds` grammar

## Prerequisites

Requires Python 3.12.

Create a `.env` file in the `backend/` directory with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_key_here
```

## Installation

From `backend/`, create the virtual environment and install the dependencies:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install \
  streamlit==1.58.0 \
  requests==2.34.2 \
  anthropic==0.113.0 \
  pydantic==2.13.4 \
  python-dotenv==1.2.2 \
  mineru==3.4.0
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
