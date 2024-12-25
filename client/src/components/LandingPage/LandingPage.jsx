import React, { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import './LandingPage.css';
import { googleAuth } from '../../Api/axios'; // API call function to your backend

const LandingPage = ({ onLoginSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(true);

  const handleGoogleLogin = () => {
    const loginUrl = 'http://localhost:8000/login-redirect?auth_provider=google-oidc';
    window.location.href = loginUrl; // Redirect to backend for Google login
  };

  return (
    <div className="home-page">
      <div className="animated-background"></div>
      <div className="login-modal">
        <h1 className="app-title">Welcome to NAVIO</h1>
        <p className="auth-prompt">Please {isSignUp ? 'Sign up' : 'Login'} with Google to continue</p>
        <button
          className="google-login-button"
          onClick={{handleGoogleLogin}}
        >
          Continue with Google
        </button>
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
