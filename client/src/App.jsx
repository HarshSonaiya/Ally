import React, { useState } from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import LandingPage from './components/LandingPage/LandingPage';
import HomePage from './components/HomePage/HomePage';
import PageNotFound from './components/PageNotFound/PageNotFound';
import CallbackPage from './components/CallbackPage/CallbackPage'; 

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('isLoggedIn') === 'true';
  });

  // Handle Google login success
  const handleLoginSuccess = (response) => {
    console.log('Google Login Success:', response);
    setIsLoggedIn(true); // Update the state to logged in
    localStorage.setItem('isLoggedIn', 'true'); // Persist login state
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    localStorage.removeItem('isLoggedIn');
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Route */}
        {!isLoggedIn && <Route path="/" element={<LandingPage onLoginSuccess={handleLoginSuccess} />} />}
        
        {/* Private Routes */}
        {isLoggedIn && (
          <>
            <Route path="/home" element={<HomePage onLogout={handleLogout} />} />
            <Route path="/" element={<Navigate to="/home" replace />} />
          </>
        )}
        {/* Callback Route for Google OAuth */}
        <Route path="/callback" element={<CallbackPage onLoginSuccess={handleLoginSuccess} />} />

        {/* Fallback */}
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
