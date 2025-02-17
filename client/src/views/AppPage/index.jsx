import React, { useEffect, useState } from 'react';
import Sidebar from '../../components/ui/Sidebar';
import MainSection from '../../components/MainSection';
import './AppPage.css';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { ChatContext, ChatProvider } from '../../context/ChatContext.jsx';

export default function AppPage() {

  const [hidden, setHidden] = useState(false);
  const navigate = useNavigate();

  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);

  localStorage.setItem('username', queryParams.get('username'));
  localStorage.setItem('email', queryParams.get('email'));
  localStorage.setItem('profile_picture', queryParams.get('profile_picture'));
  localStorage.setItem('access_token', queryParams.get('access_token'));

  const auth = localStorage.getItem('access_token');

  useEffect(() => {
    if (!auth) {
      navigate('/');
    }
  }, []);

  return (
    <ChatProvider>
    <main className='chat-page'>
      <Sidebar hidden={hidden} setHidden={setHidden} />
      <MainSection hidden={hidden} setHidden={setHidden} />
    </main>
    </ChatProvider>
  );
}