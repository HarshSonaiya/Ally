import React from 'react';
import Sidebar from '../../components/ui/Sidebar';
import MainSection from '../../components/MainSection';
import './AppPage.css';

export default function AppPage() {
  return (
    <main className='chat-page'>
      <Sidebar />
      <MainSection />
    </main>
  );
}

