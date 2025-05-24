import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import SearchBar from './SearchBar';
import { Menu, Dropdown, Badge } from 'antd';
import { UserOutlined, BellOutlined, DollarOutlined, GlobalOutlined } from '@ant-design/icons';
import '../styles/Header.css';
import LanguageSelector from './LanguageSelector';

const Header = () => {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('token');
  const cartItems = useSelector(state => state.cart.items);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const userMenu = (
    <Menu>
      <Menu.Item key="profile">
        <Link to="/profile">個人資料</Link>
      </Menu.Item>
      {/* 根據用戶角色顯示結算管理 */}
      {(user?.role === 'admin' || user?.role === 'supplier' || user?.group_mom_level > 0) && (
        <Menu.Item key="settlements">
          <Link to="/settlements">
            <DollarOutlined /> 結算管理
          </Link>
        </Menu.Item>
      )}
      <Menu.Item key="orders">
        <Link to="/orders">我的訂單</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" onClick={handleLogout}>
        登出
      </Menu.Item>
    </Menu>
  );

  return (
    <>
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            團購平台
          </Link>
          
          <div className="search-container">
            <SearchBar />
          </div>
            <div className="nav-right">
            <span className="search-icon" onClick={() => navigate('/search')}>🔍</span>
            <LanguageSelector />
            <Link to="/cart" className="cart">
              🛒
              {cartItemCount > 0 && (
                <span className="cart-count">{cartItemCount}</span>
              )}
            </Link>
            {isAuthenticated ? (
              <Dropdown overlay={userMenu} trigger={['click']}>
                <span className="user" onClick={() => setShowUserMenu(!showUserMenu)}>
                  個人中心 ▼
                </span>
              </Dropdown>
            ) : (
              <Link to="/login" className="login-btn">登入</Link>
            )}
          </div>
        </div>
      </header>
      
      <div className="category-bar">
        <div className="category">
          食品零食
          <div className="dropdown">
            <Link to="/category/snacks">休閒零食</Link>
            <Link to="/category/drinks">飲品茶類</Link>
            <Link to="/category/dried-food">乾貨食材</Link>
            <Link to="/category/health-food">保健食品</Link>
          </div>
        </div>
        <div className="category">
          美妝保養
          <div className="dropdown">
            <Link to="/category/skin-care">保養品</Link>
            <Link to="/category/makeup">彩妝品</Link>
            <Link to="/category/body-care">身體清潔</Link>
            <Link to="/category/beauty-tools">美容工具</Link>
          </div>
        </div>
        <div className="category">
          媽咪寶貝
          <div className="dropdown">
            <Link to="/category/baby-care">嬰兒用品</Link>
            <Link to="/category/mom-care">孕婦用品</Link>
            <Link to="/category/toys">玩具教具</Link>
            <Link to="/category/children-clothes">童裝童鞋</Link>
          </div>
        </div>
        <div className="category">
          生活日用
          <div className="dropdown">
            <Link to="/category/household">家居用品</Link>
            <Link to="/category/kitchenware">廚房用品</Link>
            <Link to="/category/storage">收納用品</Link>
            <Link to="/category/cleaning">清潔用品</Link>
          </div>
        </div>
        <div className="category">
          3C家電
          <div className="dropdown">
            <Link to="/category/3c">3C配件</Link>
            <Link to="/category/electronics">生活家電</Link>
            <Link to="/category/mobile">手機週邊</Link>
            <Link to="/category/computer">電腦週邊</Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default Header;