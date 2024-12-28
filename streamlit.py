import streamlit as st
import requests

# Define API base URL
API_URL = "http://localhost:8000"  # Replace with your actual backend URL

# Initialize session state for workspaces
if "workspaces" not in st.session_state:
    st.session_state.workspaces = []
if "selected_workspace_id" not in st.session_state:
    st.session_state.selected_workspace_id = None
if "participants" not in st.session_state:
    st.session_state.participants = []

def create_workspace(unique_suffix):
    """Allows the user to create a new workspace."""
    new_workspace = st.text_input(
        "Enter Workspace Name:", key=f"create_workspace_input_{unique_suffix}"
    )
    if st.button("Add Workspace", key=f"add_workspace_button_{unique_suffix}"):
        if new_workspace:
            response = requests.post(f"{API_URL}/workspace/create", json={"workspace_name": new_workspace})
            if response.status_code == 200:
                fetch_workspaces()  # Refresh workspace list after creation
                st.success(f"Workspace '{new_workspace}' created!")
            else:
                st.error(f"Failed to create workspace: {response.text}")
        else:
            st.error("Workspace name cannot be empty.")

def fetch_workspaces():
    """Fetches the list of workspaces from the backend."""
    response = requests.get(f"{API_URL}/workspace/list")
    if response.status_code == 200:
        workspaces = response.json()
        st.session_state.workspaces = [
            {"workspace_name": workspace['workspace_name'], "workspace_id": workspace['workspace_id']}
            for workspace in workspaces
        ]
    else:
        st.error(f"Failed to fetch workspaces: {response.text}")

def list_workspaces():
    """Displays a dropdown to select a workspace."""
    if not st.session_state.workspaces:
        fetch_workspaces()

    if st.session_state.workspaces:
        workspace_names = [workspace['workspace_name'] for workspace in st.session_state.workspaces]
        selected_workspace_name = st.selectbox(
            "Select Workspace", workspace_names, key="workspace_selector"
        )
        selected_workspace = next(
            workspace for workspace in st.session_state.workspaces 
            if workspace['workspace_name'] == selected_workspace_name
        )
        st.session_state.selected_workspace_id = selected_workspace['workspace_id']
    else:
        st.warning("No workspaces available. Please create one first.")

# Main Streamlit App Layout
st.title("Audio-Video Transcript Manager")

# Step 1: Create or List Workspace
st.header("1. Manage Workspaces")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Create a Workspace")
    create_workspace("column1")

with col2:
    st.subheader("List Workspace")
    list_workspaces()

# Step 2: Upload File and Add Participants
if "selected_workspace_id" in st.session_state and st.session_state.selected_workspace_id:
    st.header("2. Upload File and Participants")
    
    # File uploader (allowing for multiple file uploads)
    uploaded_files = st.file_uploader("Upload an audio or video file", type=["mp3", "mp4"], accept_multiple_files=True)
    
    # Add participant (first email will be the user's email)
    st.subheader("Participants")

    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    
    user_email = st.text_input("Enter Your Email", key="user_email_input")
    
    # If the user has entered their email, allow for other participants
    if user_email:
        if "participant_count" not in st.session_state:
            st.session_state.participant_count = 0

        # Update participant count dynamically
        new_count = st.number_input(
            "Number of Additional Participants", min_value=0, value=st.session_state.participant_count, step=1
        )
        if new_count != st.session_state.participant_count:
            st.session_state.participant_count = new_count

            # Adjust the participants list
            if len(st.session_state.participants) < st.session_state.participant_count:
                st.session_state.participants.extend(
                    [""] * (st.session_state.participant_count - len(st.session_state.participants))
                )
            elif len(st.session_state.participants) > st.session_state.participant_count:
                st.session_state.participants = st.session_state.participants[:st.session_state.participant_count]

        # Render participant input fields for other participants
        for i in range(st.session_state.participant_count):
            st.session_state.participants[i] = st.text_input(
                f"Participant {i + 1} Email", st.session_state.participants[i], key=f"participant_{i}"
            )

        # Add the user email to participants list
        participants = [user_email] + [name.strip() for name in st.session_state.participants if name.strip()]

        if st.button("Upload") and uploaded_files:
            if participants:
                # Show spinner while request is being processed
                with st.spinner("Uploading file and generating summary..."):
                    # Handle multiple or single file upload
                    if isinstance(uploaded_files, list):  # Multiple files
                        files = [
                            ("files", (uploaded_file.name, uploaded_file, uploaded_file.type or "application/octet-stream"))
                            for uploaded_file in uploaded_files
                        ]
                    else:  # Single file
                        files = [
                            ("files", (uploaded_files.name, uploaded_files, uploaded_files.type or "application/octet-stream"))
                        ]
                    
                    # Construct the body properly
                    body = {
                        "participants": participants,
                    }
                    response = requests.post(
                        f"{API_URL}/file/upload",
                        files=files,
                        params={"workspace_name": st.session_state.selected_workspace_id},  
                        data=body  
                    )

                    if response.status_code == 200:
                        st.success(f"File(s) uploaded successfully!")
                        for result in response :
                            st.session_state.filename = result.json().get("filename", "File names not available.")
                            st.session_state.summary = result.json().get("summary", "Summary not available.")
                            st.write(f"Response for file name: {st.session_state.filename}")
                            st.write(f"Summary: {st.session_state.summary}")
                            download_link = result.json().get("transcript", None)
                            if download_link:
                                st.markdown(f"[Download Transcript]({download_link})", unsafe_allow_html=True)
                            else:
                                st.write("Transcript not available for download.")
                    else:
                        st.error(f"Failed to upload file: {response.text}")
            else:
                st.error("Participants list cannot be empty.")
    else:
        st.warning("Please enter your email before adding participants.")
    
# Automatically fetch workspaces on app load
if not st.session_state.workspaces:
    fetch_workspaces()
