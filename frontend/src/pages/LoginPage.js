import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { setUser } from '../store/reducers/authReducer';
import { getProfile } from '../api';
import '../styles/LoginPage.css';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        // 登入成功後自動取得 user profile 並寫入 redux
        try {
          const user = await getProfile(data.access_token);
          dispatch(setUser(user));
        } catch (err) {
          // 若 profile 取得失敗，仍可導向 profile 頁
        }
        navigate('/profile');
      } else {
        setError(data.error || '登入失敗');
      }
    } catch (err) {
      setError('伺服器錯誤，請稍後再試');
    }
  };

  return (
    <div className="login-page">
      <h2>登入</h2>
      <form onSubmit={handleLogin} className="login-form">
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>密碼:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit">登入</button>
      </form>
      <p>
        還沒有帳號？<Link to="/register">註冊</Link>
      </p>
    </div>
  );
};

export default LoginPage;