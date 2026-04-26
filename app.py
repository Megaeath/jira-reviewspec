import streamlit as st
import pandas as pd
from utils import parse_prompts, parse_rubrics
from orchestrator import SpecReviewOrchestrator
import json
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Spec Review POC", layout="wide", initial_sidebar_state="expanded")

def apply_premium_styling():
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

        /* Global Typography and Background */
        html, body, [class*="css"] {
            font-family: 'Sarabun', sans-serif !important;
        }

        .stApp {
            background: #ffffff;
            color: #1e293b;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #f8fafc !important;
            border-right: 1px solid #e2e8f0;
        }

        /* Primary Button Styling */
        .stButton > button {
            background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.25) !important;
            width: 100% !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4) !important;
        }

        /* Text Inputs and Text Areas */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            color: #1e293b !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            padding: 0.75rem !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2) !important;
        }

        /* Expander and Tabs */
        .streamlit-expanderHeader {
            background-color: #f1f5f9 !important;
            border-radius: 8px !important;
            border: 1px solid #e2e8f0 !important;
            color: #334155 !important;
            font-weight: 600 !important;
        }

        .streamlit-expanderContent {
            border: 1px solid #e2e8f0 !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            background-color: #ffffff !important;
        }

        /* DataFrames / Tables */
        [data-testid="stTable"], [data-testid="stDataFrame"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        th {
            background-color: #f8fafc !important;
            color: #475569 !important;
            font-weight: 600 !important;
            border-bottom: 2px solid #e2e8f0 !important;
        }

        td {
            border-bottom: 1px solid #f1f5f9 !important;
            color: #334155 !important;
        }

        /* Headers with Gradient */
        h1, h2, h3 {
            background: -webkit-linear-gradient(45deg, #1d4ed8, #4f46e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: #f8fafc;
            border-radius: 8px 8px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            border: 1px solid #e2e8f0;
            border-bottom: none;
            color: #64748b;
        }

        .stTabs [aria-selected="true"] {
            background-color: #eff6ff;
            color: #2563eb !important;
            border-bottom: 2px solid #2563eb !important;
            font-weight: 600;
        }

        /* Labels */
        .stTextInput[data-testid="stTextInput"] label p, .stTextArea label p {
            font-weight: 500;
            color: #475569;
        }

        hr {
            border-color: #e2e8f0 !important;
        }
        
        /* Spinner */
        .stSpinner > div > div {
            border-top-color: #4f46e5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_premium_styling()

st.title("🛡️ AI Spec Review POC")
st.markdown("ระบบรีวิวเอกสาร Spec เปรียบเทียบประสิทธิภาพกับ Atlassian Rovo")

# --- Authentication Logic ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] == os.getenv("APP_USERNAME")
            and st.session_state["password"] == os.getenv("APP_PASSWORD")
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()
# ---------------------------

# Load prompts and rubrics into session state if not already there
if "prompts" not in st.session_state:
    try:
        st.session_state["prompts"] = parse_prompts("prompt.md")
    except Exception as e:
        st.error(f"Error loading prompt.md: {e}")
        st.session_state["prompts"] = {}

if "rubrics" not in st.session_state:
    try:
        st.session_state["rubrics"] = parse_rubrics("rovo-prompt.md")
    except Exception as e:
        st.error(f"Error loading rovo-prompt.md: {e}")
        st.session_state["rubrics"] = {}

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Use variables from environment directly, not showing in sidebar as requested
    api_key = os.getenv("GEMINI_API_KEY", "")
    conf_url = os.getenv("CONFLUENCE_URL", "")
    conf_user = os.getenv("CONFLUENCE_USER", "")
    conf_token = os.getenv("CONFLUENCE_TOKEN", "")

    # Load model list from env
    env_models_raw = os.getenv(
        "GEMINI_MODELS", '["gemini-1.5-flash", "gemini-1.5-pro"]'
    )
    try:
        available_models = json.loads(env_models_raw)
    except Exception:
        available_models = [m.strip() for m in env_models_raw.split(",")]

    env_default_model = os.getenv(
        "GEMINI_MODEL", available_models[0] if available_models else ""
    )
    model_index = (
        available_models.index(env_default_model)
        if env_default_model in available_models
        else 0
    )

    model_name = st.selectbox("Model", available_models, index=model_index)

    if st.button("🔄 Reload Prompts from File"):
        try:
            st.session_state["prompts"] = parse_prompts("prompt.md")
            st.success("Prompts reloaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.info("💡 Configuration is loaded from .env file")

# Main Prompt Configuration
with st.expander("📝 Prompt Configuration (Edit to test)"):
    st.info("คุณสามารถแก้ไข Prompt เหล่านี้เพื่อทดสอบประสิทธิภาพได้ทันที")
    for i in range(1, 6):
        st.session_state["prompts"][i] = st.text_area(
            f"Prompt {i}", value=st.session_state["prompts"].get(i, ""), height=200
        )

# Input Section
tab1, tab2 = st.tabs(["Fetch from Confluence", "Direct Text Input"])

with tab1:
    confluence_url = st.text_input("Confluence Page URL", placeholder="https://your-domain.atlassian.net/wiki/spaces/.../pages/12345")
    st.info("💡 เมื่อกดปุ่ม 'เริ่มการรีวิว' ด้านล่าง ระบบจะดึงข้อมูลจาก Confluence ให้อัตโนมัติ")

with tab2:
    spec_input = st.text_area("วางเนื้อหา Spec ที่ต้องการรีวิว (Text Only)", height=300)

# Determine source
spec_content = spec_input # Default to manual input if provided

@st.dialog("⚙️ กระบวนการรีวิว (AI Spec Review)", width="large")
def show_review_dialog(api_key, model_name, confluence_url, spec_content, conf_creds):
    # Inject JS to prevent refresh and prevent backdrop click
    st.components.v1.html("""
        <script>
            // 1. Prevent refresh
            window.parent.onbeforeunload = function(e) {
                e.preventDefault();
                e.returnValue = '';
            };
            
            // 2. Prevent closing dialog by clicking outside
            function blockOutsideClick(e) {
                const dialog = window.parent.document.querySelector('div[role="dialog"]');
                if (dialog && !dialog.contains(e.target)) {
                    e.stopPropagation();
                    e.preventDefault();
                }
            }
            const pDoc = window.parent.document;
            pDoc.addEventListener('mousedown', blockOutsideClick, true);
            pDoc.addEventListener('click', blockOutsideClick, true);
            pDoc.addEventListener('pointerdown', blockOutsideClick, true);
            window.parent._blockOutsideClick = blockOutsideClick;
        </script>
    """, height=0)

    try:
        orchestrator = SpecReviewOrchestrator(api_key, model_name)
        
        # 0. Fetch from Confluence if URL is provided and no direct content
        if confluence_url and not spec_content:
            with st.spinner("กำลังดึงข้อมูลจาก Confluence..."):
                from confluence_fetcher import ConfluenceFetcher
                conf_url, conf_user, conf_token = conf_creds
                fetcher = ConfluenceFetcher(conf_url, conf_user, conf_token)
                page_data = fetcher.get_page_content(confluence_url)
                spec_content = page_data["text"]
                
                import re
                match = re.search(r"pages/(\d+)", confluence_url)
                extracted_id = match.group(1) if match else "unknown-id"
                
                st.session_state["spec_metadata"] = {
                    "title": page_data["title"],
                    "version": page_data["version"],
                    "page_id": extracted_id
                }
                st.success(f"ดึงข้อมูลสำเร็จ: {page_data['title']}")

        # Extract page_id for logging
        page_id = "direct-input"
        if "spec_metadata" in st.session_state and "page_id" in st.session_state["spec_metadata"]:
            page_id = st.session_state["spec_metadata"]["page_id"]
        elif confluence_url:
            import re
            match = re.search(r"pages/(\d+)", confluence_url)
            if match:
                page_id = match.group(1)

        orchestrator.set_page_id(page_id)
        orchestrator.set_prompts(st.session_state["prompts"])
        orchestrator.set_rubrics(st.session_state["rubrics"])

        loader_placeholder = st.empty()
        loader_placeholder.markdown("""
            <style>
            .custom-loader-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 15px 0 25px 0;
            }
            .custom-loader {
                width: 55px;
                height: 55px;
                border: 5px solid #e2e8f0;
                border-bottom-color: #4f46e5;
                border-radius: 50%;
                display: inline-block;
                box-sizing: border-box;
                animation: rotation 1s linear infinite;
            }
            @keyframes rotation {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loader-text {
                margin-top: 15px;
                color: #4f46e5;
                font-weight: 600;
                font-size: 1.1rem;
                animation: pulse 1.5s ease-in-out infinite;
            }
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
            </style>
            <div class="custom-loader-container">
                <span class="custom-loader"></span>
                <div class="loader-text">AI is analyzing your spec...</div>
            </div>
        """, unsafe_allow_html=True)

        with st.status("🚀 กำลังเริ่มต้นกระบวนการรีวิว...", expanded=True) as status:
            def update_progress(step, msg, detail=None):
                status.update(label=f"⏳ Step {step}/5: {msg}", state="running")
                st.markdown(f"**Step {step}:** {msg}")
                if detail:
                    with st.expander("รายละเอียดเบื้องต้น (Preview)"):
                        if isinstance(detail, dict) or isinstance(detail, list):
                            st.json(detail)
                        else:
                            st.write(detail)
            
            metadata = st.session_state.get("spec_metadata", {})
            result = orchestrator.run_review(spec_content, progress_callback=update_progress, metadata=metadata)
            status.update(label="✅ การรีวิวเสร็จสมบูรณ์!", state="complete", expanded=False)
            
        loader_placeholder.empty()

        st.session_state["review_result"] = result

        # Save log
        timestamp = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
        log_filename = f"agent-conversation/review-{timestamp}"
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(f"# Review Session Log - {timestamp}\n\n")
            f.write("## Input Spec Content:\n")
            f.write(spec_content[:500] + "...\n\n")
            f.write("## Review Result:\n")
            f.write(json.dumps(result, indent=2, ensure_ascii=False))

        st.success(f"การรีวิวเสร็จสมบูรณ์! กำลังปิดหน้าต่างเพื่อแสดงผลลัพธ์... (Log: {log_filename})")
        import time
        time.sleep(2)
        st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดระหว่างการรีวิว: {e}")
        if "orchestrator" in locals() and orchestrator.last_response:
            with st.expander("🔍 ดู Raw LLM Response (เพื่อตรวจสอบ Error)"):
                st.code(orchestrator.last_response, language="json")
        print(f"\n[ERROR] Review failed: {e}")

    finally:
        # Clear the unload blocker and click blocker
        st.components.v1.html("""
            <script>
                window.parent.onbeforeunload = null;
                if (window.parent._blockOutsideClick) {
                    const pDoc = window.parent.document;
                    pDoc.removeEventListener('mousedown', window.parent._blockOutsideClick, true);
                    pDoc.removeEventListener('click', window.parent._blockOutsideClick, true);
                    pDoc.removeEventListener('pointerdown', window.parent._blockOutsideClick, true);
                    window.parent._blockOutsideClick = null;
                }
            </script>
        """, height=0)

if st.button("🚀 เริ่มการรีวิว", disabled=not api_key or (not spec_input and not confluence_url)):
    conf_creds = (conf_url, conf_user, conf_token)
    show_review_dialog(api_key, model_name, confluence_url, spec_input, conf_creds)


# Display Results
if "review_result" in st.session_state:
    res = st.session_state["review_result"]

    # 1. Summary
    st.header("1. Summary")
    summary = res.get("summary", {})
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**ประเภทเอกสาร:** {summary.get('document_type')}")
        st.write(f"**ชื่อเอกสาร:** {summary.get('document_name')}")
    with col2:
        st.write(f"**Version:** {summary.get('version')}")
        st.write(f"**การประเมินภาพรวม:** {summary.get('overall_assessment')}")

    st.subheader("จุดเด่น (Highlights)")
    for h in summary.get("highlights", []):
        st.markdown(f"- {h}")

    st.subheader("จุดที่ควรปรับปรุง (Improvements)")
    for i in summary.get("improvements", []):
        st.markdown(f"- {i}")

    # 2. Topic Review
    st.header("2. Topic Review")
    topic_df = pd.DataFrame(res.get("topic_review_table", []))
    if not topic_df.empty:
        st.table(topic_df)

    # 3. Scenario Coverage
    st.header("3. Scenario Coverage")
    scenario_df = pd.DataFrame(res.get("scenario_coverage_table", []))
    if not scenario_df.empty:
        st.table(scenario_df)

    st.markdown("---")
    st.caption(res.get("signature", "generated by AI Spec Review"))
