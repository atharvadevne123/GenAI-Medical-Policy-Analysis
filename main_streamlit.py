import os

import streamlit as st
from dotenv import load_dotenv

import langchain_helper1 as lch

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Medical Policy Analyzer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4ff 0%, #f8faff 100%);
}

/* ── Header banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a3a6e 0%, #1565c0 60%, #0d47a1 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 8px 32px rgba(21,101,192,0.25);
}
.hero-icon { font-size: 3.5rem; }
.hero-title { color: #fff; font-size: 2rem; font-weight: 700; margin: 0; line-height: 1.2; }
.hero-subtitle { color: #bbdefb; font-size: 0.95rem; margin: 0.25rem 0 0; }

/* ── Metric cards ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 120px;
    background: #fff;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 12px rgba(21,101,192,0.08);
    border-left: 4px solid #1565c0;
    text-align: center;
}
.metric-value { font-size: 1.6rem; font-weight: 700; color: #1565c0; }
.metric-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 0.05em; }

/* ── Result container ── */
.result-box {
    background: #fff;
    border-radius: 14px;
    padding: 1.5rem 2rem;
    box-shadow: 0 4px 20px rgba(21,101,192,0.07);
    border: 1px solid #e3eaf8;
    margin-bottom: 1rem;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a6e 0%, #1565c0 100%) !important;
}
[data-testid="stSidebar"] * { color: #e3f2fd !important; }
[data-testid="stSidebar"] .stTextArea textarea {
    background: rgba(255,255,255,0.1) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] label { color: #bbdefb !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(21,101,192,0.3) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(21,101,192,0.4) !important;
}

/* ── Demo badge ── */
.demo-badge {
    background: linear-gradient(135deg, #ff6f00, #ff8f00);
    color: #fff;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    display: inline-block;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ── Info bar ── */
.info-bar {
    background: linear-gradient(135deg, #e3f2fd, #bbdefb);
    border-left: 4px solid #1565c0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.88rem;
    color: #1a3a6e;
}

/* ── Table fix ── */
table { width: 100% !important; font-size: 0.85rem; }
th { background: #1565c0 !important; color: #fff !important; padding: 0.5rem 0.75rem !important; }
td { padding: 0.45rem 0.75rem !important; }
tr:nth-child(even) td { background: #f0f4ff !important; }

/* ── Footer ── */
.footer {
    text-align: center;
    color: #999;
    font-size: 0.78rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="hero-banner">
  <div class="hero-icon">🏥</div>
  <div>
    <div class="hero-title">GenAI Medical Policy Analyzer</div>
    <div class="hero-subtitle">
      AI-powered comparative analysis of medical insurance policies · Powered by OpenAI GPT-4o-mini
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Analysis Settings")
    st.markdown("---")

    medical_condition = st.text_area(
        "Medical Condition",
        placeholder="e.g. Cochlear Implant, Varicose Vein, Knee Replacement",
        max_chars=100,
        height=80,
    )

    st.markdown("### 📄 Upload Policy PDFs")
    uploaded_files = st.file_uploader(
        "Drag & drop PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    st.markdown("---")
    demo_mode = st.toggle("Demo Mode (no credentials needed)", value=False)

    st.markdown("---")
    analyze_btn = st.button("🔍 Analyze Policies", use_container_width=True)

    st.markdown("---")
    st.markdown(
        """
<div style='font-size:0.78rem; color:#90caf9;'>
<b>Data Sources</b><br>
☁️ AWS S3 bucket<br>
📁 Local PDF upload<br>
🤖 OpenAI GPT-4o-mini<br>
<br><b>Extracted Fields</b><br>
Policy Number · Title · Criteria<br>
Age Limits · Coverage · Status<br>
Prior Auth · Exclusions · Dates
</div>
""",
        unsafe_allow_html=True,
    )

# ── Credentials check ─────────────────────────────────────────────────────────
openai_api_key = os.getenv("OPENAI_API_KEY", "")

# ── Metric overview ───────────────────────────────────────────────────────────
st.markdown(
    """
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-value">18</div>
    <div class="metric-label">Data Fields</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">GPT-4o</div>
    <div class="metric-label">AI Engine</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">PDF</div>
    <div class="metric-label">Input Format</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">S3 + Local</div>
    <div class="metric-label">Data Sources</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_analyze, tab_about = st.tabs(["📊 Policy Analysis", "ℹ️ About"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tab_analyze:
    if analyze_btn:
        if not medical_condition.strip():
            st.warning("Please enter a medical condition in the sidebar before analyzing.")
        elif demo_mode:
            # ── Demo mode ──────────────────────────────────────────────────
            st.markdown(
                f'<div class="info-bar">🎭 <b>Demo Mode</b> — showing sample data for '
                f'<b>{medical_condition}</b> '
                f'<span class="demo-badge">DEMO</span></div>',
                unsafe_allow_html=True,
            )
            with st.spinner("Running AI analysis..."):
                import time
                time.sleep(1.2)

            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f"### Policy Comparison — {medical_condition}")
            st.markdown(lch.DEMO_ANALYSIS)
            st.markdown("</div>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Policies Found", "3")
            col2.metric("Insurers Compared", "3")
            col3.metric("Fields Extracted", "17 / 18")

        elif not openai_api_key and not uploaded_files:
            # ── No credentials, no files ───────────────────────────────────
            st.error(
                "No OpenAI API key found and no PDF files uploaded.\n\n"
                "**Options:**\n"
                "- Add `OPENAI_API_KEY=...` to your `.env` file and restart\n"
                "- Upload policy PDF files using the sidebar uploader\n"
                "- Toggle **Demo Mode** in the sidebar to see a sample output"
            )
        else:
            # ── Live mode ─────────────────────────────────────────────────
            bucket_name = "policydocumentschiesta"
            batch_size = 4000
            results = []

            progress = st.progress(0, text="Preparing analysis...")

            batches = list(
                lch.split_pdf_into_batches(
                    bucket_name,
                    medical_condition,
                    batch_size,
                    uploaded_files=uploaded_files if uploaded_files else None,
                )
            )

            if not batches:
                st.warning(
                    "No policy documents found. "
                    "Check your AWS credentials / S3 bucket, or upload PDF files directly."
                )
            else:
                for i, batch in enumerate(batches):
                    progress.progress(
                        int((i + 1) / len(batches) * 100),
                        text=f"Analyzing batch {i + 1} of {len(batches)}...",
                    )
                    result = lch.medical_cond_analysis(
                        medical_condition, batch, openai_api_key
                    )
                    results.append(result["policy_analysis"])

                progress.empty()

                st.success(f"Analysis complete — {len(batches)} document batch(es) processed.")

                for idx, analysis in enumerate(results):
                    with st.expander(
                        f"📋 Batch {idx + 1} — {medical_condition} Policy Analysis",
                        expanded=True,
                    ):
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown(analysis)
                        st.markdown("</div>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                col1.metric("Batches Processed", len(results))
                col2.metric("Condition", medical_condition)
                col3.metric("Fields Extracted", "18")

    else:
        # ── Idle state ────────────────────────────────────────────────────
        st.markdown(
            """
<div class="result-box" style="text-align:center; padding: 3rem;">
  <div style="font-size:3.5rem;">🏥</div>
  <h3 style="color:#1a3a6e; margin-top:0.5rem;">Ready to Analyze</h3>
  <p style="color:#666; max-width:500px; margin:0 auto;">
    Enter a <b>medical condition</b> in the sidebar, upload PDF policy documents or
    enable <b>Demo Mode</b>, then click <b>Analyze Policies</b>.
  </p>
  <br>
  <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; color:#1565c0;">
    <div>📄 <b>Upload PDFs</b><br><small>Local policy docs</small></div>
    <div>☁️ <b>S3 Bucket</b><br><small>Cloud-hosted docs</small></div>
    <div>🎭 <b>Demo Mode</b><br><small>No credentials</small></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — About
# ══════════════════════════════════════════════════════════════════════════════
with tab_about:
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown(
            """
### What This Tool Does

**GenAI Medical Policy Analyzer** automates the extraction and comparison of critical data
from medical insurance policy PDFs. It uses large language models to parse unstructured
policy text and produce a structured, side-by-side comparison table across insurers.

**Key Capabilities**
- Upload multiple policy PDFs (local or AWS S3)
- Automatically extract 18 standardized data fields per policy
- Generate a comparative table across multiple insurance providers
- Identify prior authorization requirements, exclusions, and coverage dates

**Extracted Fields**
Policy Number · Title · Age Criteria · Insurance Type · Service Type · Status ·
Effective Date · Last/Next Review · Guideline Source · States Covered ·
Prior Authorization · Exclusions · Coverage Period · Related Policies
"""
        )

    with col_r:
        st.markdown(
            """
### Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Engine | OpenAI GPT-4o-mini |
| PDF Parsing | PyPDF2 |
| Cloud Storage | AWS S3 / boto3 |
| Env Config | python-dotenv |

### Setup

```bash
git clone <repo>
pip install -r requirements.txt
cp .env.example .env
# Fill in OPENAI_API_KEY and AWS keys
streamlit run main.py
```
"""
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">GenAI Medical Policy Analyzer · Built by Atharva Devne</div>',
    unsafe_allow_html=True,
)
