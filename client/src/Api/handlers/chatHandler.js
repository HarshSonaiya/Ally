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

export default {
  createProject,
  getProjects,
};
