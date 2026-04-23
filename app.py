import streamlit as st
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Infix Assistant",
    page_icon="🤖",
    layout="wide"
)

# macOS UI/UX Styling
st.markdown("""
<style>
    /* ----- Midnight Gradient Background ----- */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #000000, #001a33, #004b7a, #000000) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 20s ease infinite !important;
    }
    [data-testid="stVerticalBlock"] { background-color: transparent !important; }

    /* ----- Sidebar ----- */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(40px) saturate(180%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    /* ----- WhatsApp-style Chat Area ----- */
    [data-testid="stChatMessageContainer"],
    [data-testid="stChatMessage"] {
        background: transparent !important;
    }

    /* User bubbles – WhatsApp green */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #005c4b !important;
        color: #e9fde0 !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 14px 18px !important;
        margin-left: auto !important;
        max-width: 72% !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        font-size: 19px !important;
        line-height: 1.6 !important;
    }

    /* Agent bubbles – dark white card */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: rgba(32, 44, 51, 0.95) !important;
        color: #e9edef !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 14px 18px !important;
        max-width: 72% !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.06);
        font-size: 19px !important;
        line-height: 1.6 !important;
    }

    /* Chat message text */
    .stChatMessage p, .stChatMessage span, .stChatMessage div {
        font-size: 19px !important;
        line-height: 1.6 !important;
    }

    /* ----- Input box ----- */
    [data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        background: rgba(32, 44, 51, 0.95) !important;
        color: #e9edef !important;
        font-size: 17px !important;
        padding: 12px 20px !important;
    }

    /* ----- Buttons ----- */
    .stButton>button {
        background-color: rgba(0,92,75,0.7);
        color: #e9fde0;
        border-radius: 10px;
        border: 1px solid rgba(0,92,75,0.9);
        font-weight: 500;
        font-size: 16px !important;
        transition: all 0.25s ease;
    }
    .stButton>button:hover {
        background-color: rgba(0,120,100,0.9);
        border-color: #00a884;
    }

    /* Checkboxes */
    .stCheckbox label { font-size: 16px !important; color: #e1e1e1 !important; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}

    /* Titles */
    .mac-title {
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #e9edef;
        margin-bottom: 20px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }

    /* Lead info card */
    .status-card {
        background: rgba(32, 44, 51, 0.6);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 12px;
        font-size: 15px;
        color: #c8d3d8;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "app_state" not in st.session_state:
    # Initial state
    st.session_state.app_state = {
        "messages": [],
        "stage": None,
        "user_data": {"name": None, "email": None, "platform": None}
    }
    
    
    with st.spinner("Initializing AI Brain & Vector Store..."):
        from main import graph
        # Update graph state with initial values
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        graph.update_state(config, st.session_state.app_state)

# Sidebar - Status and Data
with st.sidebar:
    st.markdown('<div class="mac-title">Infix</div>', unsafe_allow_html=True)
    st.markdown("### Agent Status")
    
    # Show active stage
    stage = st.session_state.app_state.get("stage")
    stage_display = stage.replace("_", " ").title() if stage else "Idle / Inquiry"
    st.info(f"**Current Flow:** {stage_display}")
    
    st.markdown("---")
    st.markdown("### Captured Lead Info")
    user_data = st.session_state.app_state.get("user_data", {})
    
    st.markdown(f"""
    <div class="status-card">
        <b>Name:</b> {user_data.get('name') or "---"}<br>
        <b>Email:</b> {user_data.get('email') or "---"}<br>
        <b>Platform:</b> {user_data.get('platform') or "---"}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.app_state = {
            "messages": [],
            "stage": None,
            "user_data": {"name": None, "email": None, "platform": None}
        }
        st.rerun()

# Main Chat Interface
st.markdown('<div class="mac-title">Infix Chat</div>', unsafe_allow_html=True)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Quick reply state handler
quick_prompt = None

if st.session_state.app_state.get("stage") == "ask_platform":
    st.markdown("<p style='color: #e1e1e1; font-size: 14px; margin-bottom: 8px; margin-top: 10px;'>Select your primary platform(s):</p>", unsafe_allow_html=True)
    
    PLATFORMS = [
        "YouTube 🔴", "Instagram 📸", "TikTok 🎵", "Facebook 🔵",
        "X (Twitter) 🐦", "LinkedIn 💼", "Twitch 💜", "Snapchat 👻",
        "Pinterest 📌", "Reddit 🤖", "Threads 🧵", "Kwai 🎬",
        "Likee 💫", "ShareChat 🇮🇳", "Moj 🎭", "Josh 🎯",
        "Chingari 🔥", "Other ✍️"
    ]
    
    if "selected_platforms" not in st.session_state:
        st.session_state.selected_platforms = []
    
    cols = st.columns(4)
    for idx, plat in enumerate(PLATFORMS):
        col = cols[idx % 4]
        is_checked = plat in st.session_state.selected_platforms
        if col.checkbox(plat, key=f"plat_{idx}", value=is_checked):
            if plat not in st.session_state.selected_platforms:
                st.session_state.selected_platforms.append(plat)
        else:
            if plat in st.session_state.selected_platforms:
                st.session_state.selected_platforms.remove(plat)
    
    other_selected = "Other ✍️" in st.session_state.selected_platforms
    other_input = ""
    if other_selected:
        other_input = st.text_input("Enter your platform name:", key="other_platform_input", placeholder="e.g. Substack, Vimeo...")
    
    if st.button("Confirm Platform(s) →", key="confirm_platforms", type="primary", use_container_width=False):
        selected = [p for p in st.session_state.selected_platforms if p != "Other ✍️"]
        if other_selected and other_input.strip():
            selected.append(other_input.strip())
        if selected:
            # Strip emojis for clean storage by joining names
            clean = ", ".join(
                p.rsplit(" ", 1)[0].strip() if any(ord(c) > 127 for c in p.split()[-1]) else p
                for p in selected
            )
            quick_prompt = clean
            st.session_state.selected_platforms = []

# Chat Input
chat_val = st.chat_input("How can I help you today?")
prompt = quick_prompt or chat_val

if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Process with Graph (Re-import is cached contextually by Python)
    from main import graph
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    inputs = {"messages": [{"role": "user", "content": prompt}]}
    
    with st.spinner("Processing..."):
        # We use stream to get the final state update comfortably
        output = None
        for step in graph.stream(inputs, config=config, stream_mode="values"):
            output = step
            
        if output and output.get("messages"):
            agent_msg = output["messages"][-1]["content"]
            st.session_state.messages.append({"role": "assistant", "content": agent_msg})
            with st.chat_message("assistant"):
                st.markdown(agent_msg)
                
            # Update local session state to reflect in UI
            st.session_state.app_state["stage"] = output.get("stage")
            st.session_state.app_state["user_data"] = output.get("user_data")
            st.rerun()
