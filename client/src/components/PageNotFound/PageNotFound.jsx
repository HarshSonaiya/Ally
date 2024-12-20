import React from 'react';
import {useNavigate} from 'react-router-dom';

import './PageNotFound.css';

const PageNotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="page-not-found">
      <h1>404 - Page Not Found</h1>
      <button onClick={() => navigate('/')}>Go to Login Page</button>
    </div>
  );
}

export default PageNotFound;