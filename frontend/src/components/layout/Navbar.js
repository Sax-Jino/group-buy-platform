import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    return (
        <nav className="navbar">
            <div className="navbar-brand">
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
                        <button onClick={() => navigate('/cart')}>購物車</button>
                        <button onClick={logout}>登出</button>
                    </>
                ) : (
                    <button onClick={() => navigate('/login')}>登入</button>
                )}
            </div>
        </nav>
    );
};

export default Navbar;