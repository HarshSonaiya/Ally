import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import './LandingPage.css';

const LandingPage = ({ onLoginSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(true);

  const handleGoogleLoginSuccess = (response) => {
    onLoginSuccess(response);
  };

  const handleLoginError = (error) => {
    console.error('Login failed:', error);
  };

  return (
    <div className="home-page">
      <div className="animated-background"></div>
      <div className="login-modal">
        <h1 className="app-title">Welcome to NAVIO</h1>
        <p className="auth-prompt">Please {isSignUp ? 'Sign up' : 'Login'} with Google to continue</p>
        <GoogleLogin
          onSuccess={handleGoogleLoginSuccess}
          onError={handleLoginError}
        />
        <button
          className="toggle-auth"
          onClick={() => setIsSignUp(!isSignUp)}
        >
          {isSignUp ? 'Already have an account? Login' : "Don't have an account? Sign up"}
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
