import { axiosRequest } from "../axios";

export function logout() {
  try {
    const response = axiosRequest({
      method: "POST",
      endpoint: "/auth/logout",
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
