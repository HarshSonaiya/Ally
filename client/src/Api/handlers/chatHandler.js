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
    files.forEach((file) => {
      formData.append("files", file); // 'files' matches the parameter name in FastAPI
    });

    // Construct query parameters
    // const query = { workspace_name: workspaceName };

    // Make the API request
    const response = await axiosRequest({
      method: "POST",
      endpoint: `/file/upload/`,
      body: formData,
      query: { workspace_name: workspaceName },
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

export async function listFiles(workspaceName) {
  try {
    const response = await axiosRequest({
      method: "GET",
      endpoint: `/file/list/`,
      query: { workspace_name: workspaceName },
    });

    return response || null;
  } catch (error) {
    if (error.response) {
      return error.response.data;
    } else {
      console.error("File List Error:", error.message);
    }
    return error;
  }
}

export async function webSearchQuery(query) {
  try {
    const response = await axiosRequest({
      method: "POST",
      endpoint: "/chat/web-search",
      body: { query, summary_type: "comprehensive" },
    });

    return response || null;
  } catch (error) {
    if (error?.response) {
      return error.response.data;
    } else {
      console.error("Web Search Error:", error.message);
    }
    return error;
  }
}

export async function chatQuery(query) {
  try {
    const response = await axiosRequest({
      method: "POST",
      endpoint: "/chat/query",
      body: query,
    });

    return response || null;
  } catch (error) {
    if (error?.response) {
      return error.response.data;
    } else {
      console.error("Chat Query Error:", error.message);
    }
    return error;
  }
}

export default {
  createProject,
  getProjects,
  uploadFiles,
  listFiles,
  webSearchQuery,
  chatQuery,
};
