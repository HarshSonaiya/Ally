import { useState } from 'react';
import Sidebar from '../../components/ui/Sidebar';
import MainSection from '../../components/MainSection';
import './AppPage.css';
import { ChatProvider } from '../../context/ChatContext.jsx';

export default function AppPage() {

  const [hidden, setHidden] = useState(false);

  return (
    <ChatProvider>
      <main className='chat-page'>
        <Sidebar hidden={hidden} setHidden={setHidden} />
        <MainSection hidden={hidden} setHidden={setHidden} />
      </main>
    </ChatProvider>
  );
}