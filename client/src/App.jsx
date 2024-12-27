import React from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import HomePage from './components/HomePage/HomePage';
import PageNotFound from './components/PageNotFound/PageNotFound';
import LandingPage from './components/LandingPage/LandingPage';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Directly render HomePage */}
        <Route path="/" element={<LandingPage />} />

        {/* Fallback route */}
        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
