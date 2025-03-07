import React from "react";
import { Route, Routes } from "react-router-dom";
import { ToastContainer } from "react-toastify";
// import HomePage from './components/HomePage/HomePage';
import PageNotFound from "./components/PageNotFound";
import LandingPage from "./views/LandingPage";
import AppPage from "./views/AppPage";
import PlaygroundPage from "./views/PlaygroundPage";

const App = () => {
  return (
    <React.Fragment>
      <Routes>
        {/* Directly render HomePage */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<AppPage />} />
        <Route path="/playground" element={<PlaygroundPage />} />

        {/* Fallback Route */}
        <Route path="*" element={<PageNotFound />} />
      </Routes>
      <ToastContainer />
    </React.Fragment>
  );
};

export default App;
