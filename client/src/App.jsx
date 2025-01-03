import React, { useEffect, useState } from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
// import HomePage from './components/HomePage/HomePage';
import PageNotFound from './components/PageNotFound';
import LandingPage from './views/LandingPage';
import AppPage from './views/AppPage';

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
    <React.Fragment>
      <Routes>
        {/* Directly render HomePage */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/app" element={<AppPage />} />

        {/* Fallback Route */}
        < Route path="*" element={<PageNotFound />} />
      </Routes>
    </React.Fragment>
  );
};

export default App;
