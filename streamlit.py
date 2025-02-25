import streamlit as st
from PIL import Image
import base64
import time


# Function to Load and Encode Logo
def get_base64_logo(logo_path):
    """Convert image to base64 encoding for embedding in HTML."""
    with open(logo_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


# Path to Logo
logo_path = r"D:\Projects\Navio\client\src\assets\logo.png"
logo_base64 = get_base64_logo(logo_path)

# Custom CSS for Sidebar Logo Placement
st.markdown(
    f"""
    <style>
        /* Background color */
        .stApp {{
            background-color: #f5f5f5;
        }}

        [data-testid="stSidebarNav"] {{
            padding-top: 0px !important;
        }}

        /* Alternatively, reduce the padding in the problematic class */
        .st-emotion-cache-kgpedg {{
            padding: 0px !important;
        }}

        .logo-container {{
            display: flex;
            width: 100%;
            align-items: center;
            margin-bottom: 50px;
        }}

        /* Sidebar logo styling */
        .logo {{
            position: relative;
            top: 0;
            left: 0;
            width: 90px;  /* Custom width */
            height: auto;   /* Maintain aspect ratio */
        }}

        /* Title Container */
        .title-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 20px;
        }}

        /* Chat Container */
        .chat-container {{
            max-width: 700px;
            margin: 20px auto;
            padding: 10px;
        }}

        /* User input box */
        .user-input {{
            background-color: #0078ff;
            color: white;
            padding: 12px 15px;
            border-radius: 15px;
            max-width: 80%;
            margin-bottom:px;
            align-self: flex-end;
        }}

        /* Assistant response */
        .bot-response {{
            background-color: #f1f1f1;
            color: black;
            padding: 12px 15px;
            border-radius: 15px;
            max-width: 80%;
            margin-bottom: 10px;
            align-self: flex-start;
        }}

        /* Chat container flexbox */
        .chat-box {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 10px;
        }}

    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_base64}" class="logo">
    </div>
    """,
    unsafe_allow_html=True,
)

# Page Title
st.markdown(
    """
    <div class="title-container">
        <h1 class='main-title'>RAG Playground</h1>
        <p class='sub-title'>Experiment with Retrieval-Augmented Generation (RAG) Models</p>       
    </div>
    """,
    unsafe_allow_html=True,
)

# Model Configuration
with st.sidebar.expander("🤖 LLM Configuration", expanded=True):
    model = st.selectbox("Choose Model", ["GPT-4", "Mistral", "Gemini"])
    temperature = st.slider(
        "Adjust Creativity Level",
        0.0,
        1.0,
        0.7,
        help="Controls randomness in responses. Higher values make outputs more diverse.",
    )
    overlap = st.slider("Set Max Token Limit", 0, 6000, 2500)

st.sidebar.markdown("---")  # Adds a separator line

# Additional Section: User Preferences
with st.sidebar.expander("🔧 User Preferences"):
    enable_debug = st.checkbox("Enable Debug Mode", False)
    show_logs = st.checkbox("Show Logs", False)

# Chat Interface
uploaded_file = st.file_uploader("📂 Upload a file", type=["pdf"])
query = st.text_input("💬 Enter your query:", placeholder="Type here...")

if st.button("Submit"):
    with st.spinner("Generating response..."):
        time.sleep(2)  # Simulating API call
        response = (
            "✅ Here is the generated response!"  # Replace with actual response logic
        )

        st.markdown(
            f"""
            <div class="chat-box">
                <div class="user-input">{query}</div>
                <div class="bot-response">{response}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
