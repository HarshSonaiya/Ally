import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000/auth",
});

export const googleAuth = async (code) => {
  try {
    console.log("Request Object code", code);
    const response = await api.post(`/google-auth`, code); 
    return response.data; 
  } catch (error) {
    console.error("API Error:", error);
    alert("Authentication failed. Please try again.");
    throw error; 
  }
};
