# AI-Powered Excel Mock Interviewer (PoC)

A lightweight Proof-of-Concept that simulates an Excel technical interview using **Streamlit**.  
The system conducts a structured, multi-turn interview, evaluates candidate answers (both conceptual and practical), manages state like a human interviewer, and generates a constructive performance summary.

---

## 🚀 Features
- **Structured Interview Flow**  
  Intro → Conceptual Questions → Excel Task → Final Summary.
- **Answer Evaluation**  
  - *Conceptual questions*: Evaluated via rule-based logic or optional LLM integration.  
  - *Practical tasks*: Excel uploads checked with `openpyxl` (formulas and results).  
- **Agentic State Management**  
  Uses `st.session_state` to track interview progress, answers, and scores.  
- **Feedback Report**  
  Generates per-question scores, strengths, areas of improvement, and overall performance.

---

## 📂 Repo Structure
    ```bash
      excel-mock-interviewer/
      ├─ app/
      │  ├─ streamlit_app.py         # Main Streamlit monolith (frontend + controller)
      │  ├─ evaluator.py             # Deterministic Excel checks (openpyxl)
      │  ├─ llm_wrapper.py           # LLM stub + optional OpenAI call
      │  └─ templates/
      │      └─ task1_template.xlsx  # auto-generated if missing
      ├─ data/
      │  └─ interviews.jsonl         # transcripts (one JSON per line)
      ├─ requirements.txt
      └─ README.md
---

## ⚡ Quickstart (Local)

1. Clone repo and create a virtual environment:
   ```bash
   git clone <repo-url>
   cd excel-mock-interviewer
   python -m venv .venv
   # Activate:
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt

2. Run the app:
   ```bash
   cd app
   streamlit run streamlit_app.py

3. Open the provided local URL in your browser.

---



  
