import React from 'react';
import Sidebar from '../../components/ui/Sidebar';
import MainSection from '../../components/Main';
import './AppPage.css';

export default function AppPage() {
  return (
    <main className='chat-page'>
      <Sidebar />
      {/* <MainSection /> */}
    </main>
  );
}

