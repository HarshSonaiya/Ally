import React from 'react'
import Sidebar from '../Sidebar/Sidebar';
import Main from '../Main/Main';

const HomePage = ({onLogout}) => {
    const handleLogout = async () => {
        try {
          const response = await fetch('http://localhost:8000/logout/', {
            method: 'GET',
            credentials: 'include',
          });
          if (response.ok) {
            onLogout(); // Notify parent of logout
          } else {
            console.error('Failed to log out');
          }
        } catch (error) {
          console.error('Error during logout:', error);
        }
    };
    return (
        <>
        <Sidebar />
        <Main />
        <button onClick={handleLogout}>Logout</button>
        </>
    );
    }

export default HomePage;