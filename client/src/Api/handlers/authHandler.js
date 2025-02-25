import { axiosRequest } from "../axios";

export async function exchangeAuthCode(authCode) {
  try {
    const response = await axiosRequest({
      method: "POST",
      endpoint: `/auth/exchange-token?auth_code=${authCode}`
    });

    if (response && response.data) {
      return [response.data.access_token, response.data.expires_at];
    } else {
      console.error("Failed to get access token");
      return null;
    }
  } catch (error) {
    console.error("Auth Code Exchange Error:", error);
    return null;
  }
}

export function logout() {
  try {
    const response = axiosRequest({
      method: "GET",
      endpoint: "/auth/logout"
    });

    return response || null;
  } catch (error) {
    console.log("error: ", error);

    if (error.response) {
      return error.response.data;
    } else {
      console.error("Sign Up Error:", error.message);
    }
    return error;
  }
}

// const handleSubmit = useCallback(async () => {
//   try {
//       const formData = new FormData();
//       files.forEach(file => {
//           formData.append('files', file); // 'files' matches the parameter name in FastAPI
//       });

//       const response = await fetch(`/api/files/upload/${currentProject.value}`, {
//           method: 'POST',
//           body: formData,
//           // Don't set Content-Type header - browser will set it automatically with boundary
//       });

//       const data = await response.json();
//       if (response.ok) {
//           onFileSelect(files);
//           setIsOpen(false);
//           setFiles([]);
//           alert('Files uploaded successfully');
//       } else {
//           throw new Error(data.detail || 'Upload failed');
//       }
//   } catch (error) {
//       console.error('Upload error:', error);
//       alert('Error uploading files: ' + error.message);
//   }
// }, [files, currentProject.value, onFileSelect]);
