import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useAuth } from '../../contexts/AuthContext';
import '../../styles/Navbar.css';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const cartItems = useSelector(state => state.cart.items);
    const cartItemCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

    return (
        <nav className="navbar">
            <div className="navbar-brand" onClick={() => navigate('/')}>
                <h1>團購平台</h1>
            </div>
            <div className="navbar-search">
                <input type="text" placeholder="搜尋商品..." />
            </div>
            <div className="navbar-actions">
                {user ? (
                    <>
                        <span>{user.role === 'big_mom' && '大團媽'}
                              {user.role === 'middle_mom' && '中團媽'}
                              {user.role === 'supplier' && '供應商'}</span>
                        <div className="cart-button" onClick={() => navigate('/cart')}>
                            🛒
                            {cartItemCount > 0 && (
                                <span className="cart-badge">{cartItemCount}</span>
                            )}
                        </div>
                        <button onClick={logout}>登出</button>
                    </>
                ) : (
                    <>
                        <button onClick={() => navigate('/login')}>登入</button>
                        <button onClick={() => navigate('/register')}>註冊</button>
                    </>
                )}
            </div>
        </nav>
    );
};

export default Navbar;