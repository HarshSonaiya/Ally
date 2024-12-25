import React, { useEffect } from 'react';

const CallbackPage = ({ onLoginSuccess }) => {
  useEffect(() => {
    const handleAuthCallback = async () => {
      const params = new URLSearchParams(window.location.search);
      const authToken = params.get('authToken');

      if (authToken) {
        try {
          // Validate the token by calling the backend
          const response = await fetch('http://localhost:8000/login/', {
            method: 'GET',
            headers: { Authorization: `Bearer ${authToken}` },
            credentials: 'include',
          });

          if (response.ok) {
            if (data.userLoggedIn) {
              onLoginSuccess(); // Notify parent of login success (update state or redirect)
            } else {
              console.error('Failed to authenticate token');
            }
          } else {
            console.error('Failed to authenticate token');
          }
        } catch (error) {
          console.error('Error during login callback:', error);
        }
      }

      // Clear the query parameters from the URL
      window.history.replaceState({}, document.title, '/');
    };

    handleAuthCallback();
  }, [onLoginSuccess]);

  return <div>Processing login...</div>;
};

export default CallbackPage;
