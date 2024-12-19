// src/App.jsx
import React, { useState } from 'react';
import Sidebar from './components/Sidebar/Sidebar';
import Main from './components/Main/Main';
import LandingPage from './components/LandingPage/LandingPage';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  const handleLoginSuccess = (response) => {
    console.log('Google Login Success:', response);
    // Handle the response (you can send the token to the backend if needed)
    setUserInfo(response);
    setIsLoggedIn(true); // Update login state
  };

  return (
    <>
      {!isLoggedIn ? (
        <LandingPage onLoginSuccess={handleLoginSuccess} /> // Show HomePage with Google login/signup
      ) : (
        <>
          <Sidebar />
          <Main />
        </>
      )}
    </>
  );
};

export default App;
