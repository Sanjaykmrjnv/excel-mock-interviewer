import streamlit as st
import tempfile, os, json, uuid, datetime
from evaluator import evaluate_submission
from llm_wrapper import llm_evaluate

TEMPLATES_DIR = "templates"
DATA_DIR = "../data"
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Excel Mock Interviewer — PoC", layout="centered")

st.title("AI-Powered Excel Mock Interviewer — PoC")

if 'interview' not in st.session_state:
    st.session_state.interview = {
        "id": str(uuid.uuid4()),
        "started_at": datetime.datetime.utcnow().isoformat(),
        "stage": "intro",
        "qa": [],
        "deterministic": None,
        "llm_feedback": None
    }

def save_transcript(obj: dict):
    path = os.path.join(DATA_DIR, "interviews.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")

def generate_template(path):
    # create a very simple workbook programmatically so the user can download
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Qty", "Price", "Total"])  # header
    # sample rows
    ws.append([2, 100, None])
    ws.append([5, 9.99, None])
    ws.append([1, 250, None])
    # Put a formula for G1 example (we'll instruct candidate to fill Total col and fill G1)
    ws["G1"] = None
    wb.save(path)

# Intro
if st.session_state.interview['stage'] == 'intro':
    st.markdown("**Instructions:** This is a short Excel skills assessment. You'll answer two quick conceptual questions and complete a small workbook task. Timebox ~10 minutes for demo.")
    if st.button("Start interview"):
        st.session_state.interview['stage'] = 'concept'
        st.rerun()

# Concept questions
if st.session_state.interview['stage'] == 'concept':
    st.header("Part 1 — Conceptual questions")
    q1 = st.text_area("Q1. What does `$A$1` mean in Excel? (1-2 sentences)", key="q1")
    q2 = st.text_area("Q2. When would you use a pivot table? (1-2 sentences)", key="q2")
    if st.button("Submit answers"):
        st.session_state.interview['qa'].append({"q":"$A$1 meaning", "a": q1, "ts": datetime.datetime.utcnow().isoformat()})
        st.session_state.interview['qa'].append({"q":"Pivot use", "a": q2, "ts": datetime.datetime.utcnow().isoformat()})
        # LLM quick scoring for concept Q1
        llm_q1 = llm_evaluate("concept", q1)
        st.session_state.interview['llm_feedback'] = {"q1": llm_q1}
        st.session_state.interview['stage'] = 'task'
        st.rerun()

# Task / Upload
if st.session_state.interview['stage'] == 'task':
    st.header("Part 2 — Hands-on workbook task")
    st.markdown("Download the template, fill formulas, and upload the completed workbook.")
    template_path = os.path.join(TEMPLATES_DIR, "task1_template.xlsx")
    if not os.path.exists(template_path):
        generate_template(template_path)
    with open(template_path, "rb") as f:
        st.download_button("Download template", data=f, file_name="task1_template.xlsx")
    uploaded = st.file_uploader("Upload your completed workbook (.xlsx)", type=["xlsx"])
    if uploaded:
        # save tmp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name
        det = evaluate_submission(tmp_path)
        st.session_state.interview['deterministic'] = det
        # LLM-based feedback for workbook
        llm_w = llm_evaluate("workbook", det)
        st.session_state.interview['llm_feedback']["workbook"] = llm_w
        st.session_state.interview['stage'] = 'summary'
        # persist
        st.session_state.interview['finished_at'] = datetime.datetime.utcnow().isoformat()
        save_transcript(st.session_state.interview)
        st.success("Uploaded and evaluated. See summary below.")
        st.rerun()

# Summary
if st.session_state.interview['stage'] == 'summary':
    st.header("Interview Summary")
    st.json(st.session_state.interview)
    # show scores (simple fusion)
    det_pass = st.session_state.interview['deterministic']['pass']
    det_score = 100 if det_pass else max(0, 50 - len(st.session_state.interview['deterministic']['row_mismatches'])*10)
    llm_score = st.session_state.interview['llm_feedback'].get('workbook', {}).get('score', 0) * 20
    fused = int(0.6 * det_score + 0.4 * llm_score)
    st.metric("Fused score (0-100)", fused)
    st.markdown("**LLM feedback (concept q1):**")
    st.write(st.session_state.interview['llm_feedback'].get('q1'))
    st.markdown("**LLM feedback (workbook):**")
    st.write(st.session_state.interview['llm_feedback'].get('workbook'))
    if st.button("Start new interview"):
        st.session_state.interview = {
            "id": str(uuid.uuid4()),
            "started_at": datetime.datetime.utcnow().isoformat(),
            "stage": "intro",
            "qa": [],
            "deterministic": None,
            "llm_feedback": None
        }
        st.rerun()
