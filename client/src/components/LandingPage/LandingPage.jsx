import React, { useState } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for redirecting
import './LandingPage.css';
import { googleAuth } from '../../Api/axios';

const LandingPage = ({ onLoginSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(true);
  const navigate = useNavigate(); // Initialize navigate for programmatic redirection

  // Initialize Google login
  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        console.log(tokenResponse.code); // The authorization code
        // Instead of sending the code to the backend directly, we'll redirect to /callback
        navigate(`/callback?code=${tokenResponse.code}`);
      } catch (error) {
        console.error('API Error:', error);
        alert('Authentication failed. Please try again.');
      }
    },
    onError: (error) => {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    },
    flow: 'auth-code', // Using the authorization code flow
  });

  return (
    <div className="home-page">
      <div className="animated-background"></div>
      <div className="login-modal">
        <h1 className="app-title">Welcome to NAVIO</h1>
        <p className="auth-prompt">Please {isSignUp ? 'Sign up' : 'Login'} with Google to continue</p>
        <button
          className="google-login-button"
          onClick={() => login()}
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
