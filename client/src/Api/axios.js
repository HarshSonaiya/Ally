import axios from "axios";

// const BASE_URL = "http://localhost:8000";
const BASE_URL = import.meta.env.VITE_BASE_URL;

const axiosInstance = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  // timeout: 10000,
});

axiosInstance.interceptors.request.use(function accessTokenInterceptor(config) {
  const accessToken = localStorage.getItem("access_token");

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

axiosInstance.interceptors.response.use(
  (response) => {
    console.log("Full response: ", response);
    return response.data
  },
  function errorHandlingInterceptor(error) {
    console.error(error)
    if (axios.isCancel(error)) {
      console.error("Request canceled:", error.message);
      return Promise.reject(null); // Treat canceled requests differently if needed
    }

    if (error.response?.status === 401) {
      // Clear stored tokens 
      localStorage.removeItem("access_token");
      
      // Notify user about authentication failure
      const errorMessage =
        error.response.data?.error || "Authentication failed. Please log in again.";

      // Display the custom error message
      alert(errorMessage);

      window.location.href = "/"; // Redirect to login page
    }

    // const status = error.response?.status;
    // const errorMessage = error.response?.data?.message;

    // if (status === 400) {
    //   const message = Array.isArray(errorMessage)
    //     ? errorMessage[0]
    //     : errorMessage;
    //   // toast.error(message);
    //   return Promise.reject({ error: true, message });
    // }

    console.error("Error making request:", error);
    return Promise.reject(error);
  }
);

let controller;
let previousEndpoint;

export const axiosRequest = async ({
  method = "GET",
  endpoint = "",
  headers = {},
  body = {},
  query = {},
}) => {
  // Cancel previous request if it's the same endpoint
  if (controller && previousEndpoint === endpoint) {
    controller.abort();
  }
  controller = new AbortController();
  previousEndpoint = endpoint;

  //* Configure request
  const config = {
    method,
    url: endpoint,
    headers,
    params: query,
    data: body,
    signal: controller.signal,
  };

  // Send request
  const response = await axiosInstance(config);
  return response;
};
