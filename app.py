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
        /* Import Fonts */
        @import url('https://api.fontshare.com/v2/css?f[]=general-sans@700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&family=JetBrains+Mono&display=swap');

        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif !important;
            color: #0A0A0A !important;
        }

        .stApp {
            background-color: #FAFAFA !important;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'General Sans', sans-serif !important;
            font-weight: 700 !important;
            color: #0A0A0A !important;
            letter-spacing: -0.03em !important;
            background: none !important;
            -webkit-text-fill-color: initial !important;
        }

        h1 { font-size: 60px !important; }
        h2 { font-size: 32px !important; }
        h3 { font-size: 24px !important; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E8E8EC !important;
        }

        /* Buttons */
        .stButton > button {
            background-color: #6366F1 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 10px 16px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            transition: all 200ms ease !important;
            box-shadow: none !important;
            width: 100% !important;
        }

        .stButton > button:hover {
            background-color: #4F46E5 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(99,102,241,0.35) !important;
        }

        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* Inputs & Textareas */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #FFFFFF !important;
            border: 1px solid #E8E8EC !important;
            color: #0A0A0A !important;
            border-radius: 6px !important;
            padding: 10px 14px !important;
            font-size: 14px !important;
            transition: all 200ms ease !important;
        }

        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
        }

        /* Cards / Expanders */
        .streamlit-expanderHeader {
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            border: 1px solid #E8E8EC !important;
            color: #0A0A0A !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
        }

        .streamlit-expanderContent {
            border: 1px solid #E8E8EC !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            background-color: #FFFFFF !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 16px;
            background-color: transparent;
            border-bottom: 1px solid #E8E8EC;
        }

        .stTabs [data-baseweb="tab"] {
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            color: #6B6B6B !important;
            background-color: transparent !important;
            border: none !important;
            padding: 12px 0 !important;
        }

        .stTabs [aria-selected="true"] {
            color: #6366F1 !important;
            border-bottom: 2px solid #6366F1 !important;
        }

        /* DataFrames / Tables */
        [data-testid="stTable"], [data-testid="stDataFrame"] {
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid #E8E8EC !important;
            padding: 8px !important;
        }

        th {
            background-color: #FAFAFA !important;
            color: #6B6B6B !important;
            font-weight: 500 !important;
            border-bottom: 1px solid #E8E8EC !important;
            text-transform: uppercase;
            font-size: 11px !important;
            letter-spacing: 0.05em;
        }

        td {
            border-bottom: 1px solid #FAFAFA !important;
            color: #0A0A0A !important;
            font-size: 14px !important;
        }

        /* Code Blocks */
        code {
            font-family: 'JetBrains Mono', monospace !important;
            background-color: #F1F1F4 !important;
            border-radius: 4px !important;
            padding: 2px 4px !important;
        }

        /* Custom Genesis Card */
        .genesis-card {
            background-color: #FFFFFF;
            border: 1px solid #E8E8EC;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            transition: all 200ms ease;
        }

        .genesis-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        }

        /* Custom Loader */
        .stSpinner > div > div {
            border-top-color: #6366F1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_premium_styling()

st.title("🛡️ AI Spec Review")
st.markdown('<p style="font-family: \'DM Sans\'; color: #6B6B6B; font-size: 18px; margin-top: -20px;">Editorial Precision Interface by <span style="color: #20970B; font-weight: 700;">DESIGN.md</span></p>', unsafe_allow_html=True)

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
        st.markdown('<div class="genesis-card" style="max-width: 400px; margin: 100px auto;">', unsafe_allow_html=True)
        st.subheader("Welcome Back")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.markdown('<div class="genesis-card" style="max-width: 400px; margin: 100px auto;">', unsafe_allow_html=True)
        st.subheader("Welcome Back")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 User not known or password incorrect")
        st.markdown('</div>', unsafe_allow_html=True)
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

if "single_prompt" not in st.session_state:
    try:
        with open("rovo-prompt-optimized.md", "r", encoding="utf-8") as f:
            st.session_state["single_prompt"] = f.read()
    except Exception as e:
        st.session_state["single_prompt"] = ""

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
            st.session_state["rubrics"] = parse_rubrics("rovo-prompt.md")
            with open("rovo-prompt-optimized.md", "r", encoding="utf-8") as f:
                st.session_state["single_prompt"] = f.read()
            st.success("Prompts & Rubrics reloaded!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.info("💡 Configuration is loaded from .env file")

# Main Prompt Configuration
with st.expander("📝 Prompt Configuration (Edit to test)"):
    st.info("คุณสามารถแก้ไข Prompt เหล่านี้เพื่อทดสอบประสิทธิภาพได้ทันที")
    
    st.markdown("### 🔄 Orchestrated Mode Prompts")
    for i in range(1, 6):
        st.session_state["prompts"][i] = st.text_area(
            f"Step {i}: {st.session_state['prompts'].get(i, '').split('\\n')[0][:50]}...", 
            value=st.session_state["prompts"].get(i, ""), 
            height=150,
            key=f"p_{i}"
        )
    
    st.divider()
    st.markdown("### ⚡ Single Request Mode Prompt (Rovo Style)")
    st.session_state["single_prompt"] = st.text_area(
        "Optimized Rovo Prompt",
        value=st.session_state.get("single_prompt", ""),
        height=400,
        key="p_single"
    )

# Input Section
tab1, tab2, tab3 = st.tabs(["🔄 Orchestrated Review", "✍️ Direct Text Input", "⚡ Single Request (Rovo Style)"])

review_mode = "orchestrated"
confluence_url = ""
spec_input = ""

with tab1:
    confluence_url = st.text_input("Confluence Page URL", placeholder="https://your-domain.atlassian.net/wiki/spaces/.../pages/12345", key="conf_url_1")
    st.info("💡 โหมดนี้จะใช้ AI หลายตัวทำงานร่วมกัน (Multi-Agent) เพื่อความละเอียดสูงสุด")
    if st.button("🚀 เริ่มการรีวิว (Orchestrated)", key="btn_orch", use_container_width=True):
        if not confluence_url:
            st.error("กรุณาระบุ Confluence Page URL")
        else:
            review_mode = "orchestrated"
            st.session_state["review_mode"] = "orchestrated"
            st.session_state["active_url"] = confluence_url
            st.session_state["active_text"] = ""
            st.session_state["show_dialog"] = True

with tab2:
    spec_input = st.text_area("วางเนื้อหา Spec ที่ต้องการรีวิว (Text Only)", height=300, key="text_input_2")
    st.info("💡 โหมดนี้สำหรับรีวิวเนื้อหาที่ไม่ได้อยู่ใน Confluence")
    if st.button("🚀 เริ่มการรีวิว (Direct Text)", key="btn_text", use_container_width=True):
        if not spec_input:
            st.error("กรุณาวางเนื้อหา Spec")
        else:
            review_mode = "orchestrated"
            st.session_state["review_mode"] = "orchestrated"
            st.session_state["active_url"] = ""
            st.session_state["active_text"] = spec_input
            st.session_state["show_dialog"] = True

with tab3:
    confluence_url_single = st.text_input("Confluence Page URL (Single Request)", placeholder="https://your-domain.atlassian.net/wiki/spaces/.../pages/12345", key="conf_url_3")
    st.info("💡 โหมดนี้จะส่งคำขอเดียว (Single Request) โดยใช้ Prompt ที่ปรับแต่งให้กระชับ เพื่อความรวดเร็ว")
    if st.button("⚡ เริ่มการรีวิว (Single Request)", key="btn_single", use_container_width=True):
        if not confluence_url_single:
            st.error("กรุณาระบุ Confluence Page URL")
        else:
            review_mode = "single"
            st.session_state["review_mode"] = "single"
            st.session_state["active_url"] = confluence_url_single
            st.session_state["active_text"] = ""
            st.session_state["show_dialog"] = True

@st.dialog("⚙️ กระบวนการรีวิว (AI Spec Review)", width="large")
def show_review_dialog(api_key, model_name, confluence_url, spec_content, conf_creds, mode="orchestrated"):
    # Inject JS (omitted for brevity in prompt but I should keep it)
    st.components.v1.html("""
        <script>
            window.parent.onbeforeunload = function(e) {
                e.preventDefault();
                e.returnValue = '';
            };
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
                    "page_id": extracted_id,
                    "url": confluence_url
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
        
        if mode == "orchestrated":
            orchestrator.set_prompts(st.session_state["prompts"])
            orchestrator.set_rubrics(st.session_state["rubrics"])

            loader_placeholder = st.empty()
            loader_placeholder.markdown("""
                <div class="custom-loader-container">
                    <span class="custom-loader"></span>
                    <div class="loader-text">Orchestrating multi-agent review...</div>
                </div>
            """, unsafe_allow_html=True)

            with st.status("🚀 กำลังเริ่มต้นกระบวนการรีวิวแบบละเอียด...", expanded=True) as status:
                def update_progress(step, msg, detail=None):
                    status.update(label=f"⏳ Step {step}/5: {msg}", state="running")
                    st.markdown(f"**Step {step}:** {msg}")
                
                metadata = st.session_state.get("spec_metadata", {})
                result = orchestrator.run_review(spec_content, progress_callback=update_progress, metadata=metadata)
                status.update(label="✅ การรีวิวเสร็จสมบูรณ์!", state="complete", expanded=False)
        else:
            # Single Request mode
            loader_placeholder = st.empty()
            loader_placeholder.markdown("""
                <div class="custom-loader-container">
                    <span class="custom-loader"></span>
                    <div class="loader-text">Single request (Rovo Style) review...</div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("⚡ กำลังประมวลผลคำขอเดียว (Single Request)..."):
                metadata = st.session_state.get("spec_metadata", {})
                optimized_prompt = st.session_state.get("single_prompt", "")
                result = orchestrator.run_single_request_review(spec_content, optimized_prompt, metadata=metadata)
                
            st.success("⚡ รีวิวเสร็จสิ้น (Single Request)")

        loader_placeholder.empty()
        st.session_state["review_result"] = result
        st.session_state["review_mode_result"] = mode

        # Save log if in dev environment
        app_env = os.getenv("APP_ENV", "dev")
        if app_env == "dev":
            os.makedirs("app-log", exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
            log_filename = f"app-log/review-{timestamp}"
            with open(log_filename, "w", encoding="utf-8") as f:
                f.write(f"# Review Session Log ({mode}) - {timestamp}\n\n")
                if isinstance(result, str):
                    f.write(result)
                else:
                    f.write(json.dumps(result, indent=2, ensure_ascii=False))
            st.success(f"บันทึก Log เรียบร้อย: {log_filename}")
        
        import time
        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดระหว่างการรีวิว: {e}")
            
        if 'loader_placeholder' in locals():
            loader_placeholder.empty()

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

# Handle dialog trigger
if st.session_state.get("show_dialog"):
    # Clear the flag so it doesn't loop
    st.session_state["show_dialog"] = False
    
    # Check dependencies
    if not api_key:
        st.error("Missing Gemini API Key!")
    else:
        # Call the dialog
        conf_creds = (conf_url, conf_user, conf_token)
        mode = st.session_state.get("review_mode", "orchestrated")
        url = st.session_state.get("active_url", "")
        text = st.session_state.get("active_text", "")
        
        # Call the dialog function
        show_review_dialog(api_key, model_name, url, text, conf_creds, mode)

# Display Results
if "review_result" in st.session_state:
    res = st.session_state["review_result"]
    mode = st.session_state.get("review_mode_result", "orchestrated")
    
    if mode == "single":
        st.markdown('<div class="genesis-card">', unsafe_allow_html=True)
        st.header("⚡ Single Request Review Result")
        st.markdown(res)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 1. Summary
        st.markdown('<div class="genesis-card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Topic Review
        st.markdown('<div class="genesis-card">', unsafe_allow_html=True)
        st.header("2. Topic Review")
        import pandas as pd
        topic_df = pd.DataFrame(res.get("topic_review_table", []))
        if not topic_df.empty:
            st.table(topic_df)
        st.markdown('</div>', unsafe_allow_html=True)

        # 3. Scenario Coverage
        st.markdown('<div class="genesis-card">', unsafe_allow_html=True)
        st.header("3. Scenario Coverage")
        scenario_df = pd.DataFrame(res.get("scenario_coverage_table", []))
        if not scenario_df.empty:
            st.table(scenario_df)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.caption(res.get("signature", "generated by AI Spec Review"))
