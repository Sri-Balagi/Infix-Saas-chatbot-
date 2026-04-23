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
    /* Midnight Sea Dynamic Background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #000000, #001a33, #004b7a, #000000) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 20s ease infinite !important;
        color: white !important;
    }
    
    /* Ensure main area content is transparent to show background */
    [data-testid="stVerticalBlock"] {
        background-color: transparent !important;
    }
    
    /* Sidebar Styling - Glassmorphism Dark */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.6) !important;
        backdrop-filter: blur(40px) saturate(180%);
        -webkit-backdrop-filter: blur(40px) saturate(180%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Message styling */
    .stChatMessage {
        border-radius: 18px !important;
        padding: 12px 18px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* User message bubble - SF Blue */
    [data-testid="stChatMessage"]:nth-child(even) {
        background-color: #007aff !important;
        color: white !important;
    }
    
    /* Agent message bubble - Dark Translucent */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Input area styling */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(40, 40, 40, 0.8) !important;
        color: white !important;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(0, 122, 255, 0.5);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Title */
    .mac-title {
        font-size: 28px;
        font-weight: 600;
        letter-spacing: -0.5px;
        color: #ffffff;
        margin-bottom: 24px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .status-card {
        background: rgba(40, 40, 40, 0.4);
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 12px;
        font-size: 14px;
        color: #e1e1e1;
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
