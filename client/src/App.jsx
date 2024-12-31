import React, { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes, Navigate } from 'react-router-dom';
import HomePage from './components/HomePage/HomePage';
import PageNotFound from './components/PageNotFound/PageNotFound';
import LandingPage from './components/LandingPage/LandingPage';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check for user login status localStorage 
  useEffect(() => {
    const userToken = localStorage.getItem('userToken');
    setIsLoggedIn(!!userToken);
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Directly render HomePage */}
        {/* <Route path="/" element={<LandingPage />} /> */}
        <Route path="/" element={<LandingPage />} />

        {/* Fallback Route */}
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
