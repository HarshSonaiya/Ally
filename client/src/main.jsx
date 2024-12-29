import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

import { GoogleOAuthProvider } from '@react-oauth/google';

const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || "983280027280-gg39il92sm9q7robp219li8mvt0kb56t.apps.googleusercontent.com";

if (!clientId) {
  console.error("Google Client ID is missing. Make sure REACT_APP_GOOGLE_CLIENT_ID is set in the .env file.");
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={clientId}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)