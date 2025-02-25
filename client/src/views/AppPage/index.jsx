import { useEffect, useState, useRef } from 'react';
import Sidebar from '../../components/ui/Sidebar';
import MainSection from '../../components/MainSection';
import './AppPage.css';
import { useNavigate } from 'react-router-dom';
import { ChatProvider } from '../../context/ChatContext.jsx';
import { exchangeAuthCode } from '../../Api/handlers/authHandler.js';

export default function AppPage() {

  const [hidden, setHidden] = useState(false);
  const navigate = useNavigate();
  const hasRun = useRef(false);

  useEffect(() => {
    const checkAuthCodeAndExchange = async () => {
      if (hasRun.current) return;  // Stop second execution
      hasRun.current = true;

      const urlParams = new URLSearchParams(window.location.search);
      const authCode = urlParams.get("auth_code");

      if (authCode) {
        const [accessToken, expiresAt] = await exchangeAuthCode(authCode);
        
        if (accessToken) {
          localStorage.setItem("access_token", accessToken);  // Store token
          localStorage.setItem("expires_at", expiresAt); // Store expiry time of the access token
          window.history.replaceState({}, document.title, "/chat");  // Clean URL
        } else {
          navigate("/"); // Redirect to login page if token exchange fails
        }
      } else {
        const storedToken = localStorage.getItem("access_token");
        if (!storedToken) {
          navigate("/");  // Redirect if no token is available
        }
      }
    };

    checkAuthCodeAndExchange();
  }, [navigate]);

  return (
    <ChatProvider>
      <main className='chat-page'>
        <Sidebar hidden={hidden} setHidden={setHidden} />
        <MainSection hidden={hidden} setHidden={setHidden} />
      </main>
    </ChatProvider>
  );
}