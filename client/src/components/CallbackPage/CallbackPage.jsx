import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { googleAuth } from '../../Api/axios'; // Your function for backend communication

const CallbackPage = ({ onLoginSuccess }) => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const code = searchParams.get('code'); // Extract the code from URL

  useEffect(() => {
    if (code) {
      // Send the code to your backend to exchange it for an access token
      const exchangeCode = async () => {
        try {
          const response = await googleAuth({ code }); // Backend call with code
          console.log('Login Successful:', response.data);
          onLoginSuccess(response.data); // Handle successful login
        } catch (error) {
          console.error('Error exchanging code:', error);
          alert('Authentication failed. Please try again.');
        }
      };
      exchangeCode();
    }
  }, [code, onLoginSuccess]);

  return (
    <div>
      <h2>Logging you in...</h2>
      <p>Please wait while we process your authentication.</p>
    </div>
  );
};

export default CallbackPage;
