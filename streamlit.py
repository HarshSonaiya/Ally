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
if "file_id" not in st.session_state:
    st.session_state.file_id = None

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

# Fetch files from the selected workspace
def fetch_files(workspace_id):
    """Fetches the list of files for the selected workspace."""
    response = requests.get(f"{API_URL}/file/list", params={"workspace_name": workspace_id})
    if response.status_code == 200:
        files = response.json()
        return files
    else:
        st.error(f"Failed to fetch files: {response.text}")
        return []

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

# Step 2: Upload File
if "selected_workspace_id" in st.session_state and st.session_state.selected_workspace_id:
    st.header("2. Upload File")
    
    # File uploader (allowing for multiple file uploads)
    uploaded_files = st.file_uploader("Upload an audio or video file", type=["mp3", "mp4"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("Upload"):
            with st.spinner("Uploading file..."):
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
                
                # Construct the body for file upload request
                body = {}
                response = requests.post(
                    f"{API_URL}/file/upload",
                    files=files,
                    params={"workspace_name": st.session_state.selected_workspace_id},
                    data=body
                )

                if response.status_code == 200:
                    st.success(f"File(s) uploaded successfully!")
                    
                    # Refresh the file list after upload
                    st.session_state.files = fetch_files(st.session_state.selected_workspace_id)
                else:
                    st.error(f"Failed to upload file: {response.text}")

# Step 3: Existing Files (Select File for Summary Generation)
if "selected_workspace_id" in st.session_state and st.session_state.selected_workspace_id:
    st.header("3. Existing Files")

    # Fetch existing files for the selected workspace
    files = fetch_files(st.session_state.selected_workspace_id)

    if files:
        selected_file_name = st.selectbox("Select a File for Summary Generation", [file["filename"] for file in files])
        selected_file = next(file for file in files if file["filename"] == selected_file_name)
        st.session_state.file_id = selected_file["file_id"]

        # Option to generate a summary for the selected file
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                response = requests.post(
                    f"{API_URL}/generate-summary",
                    json={
                        "workspace_name": st.session_state.selected_workspace_id,
                        "file_id": st.session_state.file_id
                    }
                )

                if response.status_code == 200:
                    st.success("Summary generated successfully!")
                    summary = response.json().get("summary", "No summary available.")
                    st.write(f"Summary: {summary}")
                else:
                    st.error(f"Failed to generate summary: {response.text}")

# Step 4: Generate Custom Summary
if "file_id" in st.session_state and st.session_state.file_id:
    st.header("4. Generate Custom Summary")

    start_time = st.number_input("Enter Start Time (in seconds):", min_value=0, value=0)
    end_time = st.number_input("Enter End Time (in seconds):", min_value=start_time, value=start_time + 60)

    if st.button("Generate Custom Summary"):
        with st.spinner("Generating custom summary..."):
            # Send POST request to generate the custom summary
            response = requests.post(
                f"{API_URL}/custom-summary",
                json={
                    "workspace_name": st.session_state.selected_workspace_id,
                    "file_id": st.session_state.file_id,
                    "start_time": start_time,
                    "end_time": end_time
                }
            )

            if response.status_code == 200:
                st.success("Custom summary generated successfully!")
                summary = response.json().get("summary", "No summary available.")
                st.write(f"Custom Summary: {summary}")
            else:
                st.error(f"Failed to generate summary: {response.text}")

# Step 5: Add Participants and Send Email (after summary generation)
if "file_id" in st.session_state and st.session_state.file_id:
    st.header("5. Add Participants and Send Email")

    participants = []
    user_email = st.text_input("Enter Your Email")

    if user_email:
        participants.append(user_email)

    if st.button("Send Email"):
        # Send POST request to send email with summary and participants
        response = requests.post(
            f"{API_URL}/send-email",
            json={
                "workspace_name": st.session_state.selected_workspace_id,
                "file_id": st.session_state.file_id,
                "summary": "The custom summary goes here.",  # You should use the generated summary here
                "participants": participants
            }
        )

        if response.status_code == 200:
            st.success("Email sent successfully!")
        else:
            st.error(f"Failed to send email: {response.text}")
