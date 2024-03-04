import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import './NavigationBar.css';

const NavigationBar = () => {
  const location = useLocation();
  return (
    <nav className='navbar'>
      <ul className="navList">
        <li>
          <NavLink to="/chat" className={location.pathname === '/chat' ? 'active-link' : ''}>
            ChatBot
          </NavLink>
        </li>
        <li>
          <NavLink to="/code" className={location.pathname === '/code' ? 'active-link' : ''}>
            CodeBot
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default NavigationBar;