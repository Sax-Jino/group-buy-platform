import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import '../styles/Header.css';

const Header = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('token');
  const cartItems = useSelector(state => state.cart.items);
  
  const cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0);

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
          {isAuthenticated && (
            <>
              <Link to="/recipients">收貨人</Link>
              <Link to="/profile">個人資料</Link>
              <Link to="/cart" className="cart-link">
                購物車
                {cartItemCount > 0 && (
                  <span className="cart-badge">{cartItemCount}</span>
                )}
              </Link>
              <button onClick={handleLogout} className="logout-btn">登出</button>
            </>
          )}
          {!isAuthenticated && (
            <Link to="/login">登入</Link>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;