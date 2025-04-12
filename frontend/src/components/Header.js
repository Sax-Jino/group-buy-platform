import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../styles/Header.css';

const Header = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('token'); // 簡單檢查是否登入

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-container">
        <Link to="/" className="logo">團購平台</Link>
        <nav className="nav-menu">
          <Link to="/products">商品</Link>
          <Link to="/orders">訂單</Link>
          <Link to="/collaborations">協作</Link>
          {isAuthenticated ? (
            <>
              <Link to="/profile">個人資料</Link>
              <button onClick={handleLogout} className="logout-btn">登出</button>
            </>
          ) : (
            <Link to="/login">登入</Link>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;