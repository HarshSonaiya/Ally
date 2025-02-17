import { axiosRequest } from "../axios";

export function createProject(project) {
  try {
    const response = axiosRequest({
      method: "POST",
      endpoint: "/workspace/create",
      body: project,
    });

    return response || null;
  } catch (error) {
    if (error.response) {
      return error.response.data;
    } else {
      console.error("Sign Up Error:", error.message);
    }
    return error;
  }
}

export function getProjects() {
  try {
    const response = axiosRequest({
      method: "GET",
      endpoint: "/workspace/list",
    });

    return response || null;
  } catch (error) {
    if (error.response) {
      return error.response.data;
    } else {
      console.error("Sign Up Error:", error.message);
    }
    return error;
  }
}

export async function uploadFiles(files, workspaceName) {
  try {
    const formData = new FormData();
    
    // Append files to FormData
    files.forEach((file) => formData.append("files", file));

    // Construct query parameters
    const query = { workspace_name: workspaceName };

    // Make the API request
    const response = await axiosRequest({
      method: "POST",
      endpoint: `/file/upload/${workspaceName}`,
      body: formData, 
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response || null;
  } catch (error) {
    if (error.response) {
      return error.response.data;
    } else {
      console.error("File Upload Error:", error.message);
    }
    return error;
  }
}

export default {
  createProject,
  getProjects,
  uploadFiles,
};
