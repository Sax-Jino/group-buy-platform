import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import '../styles/LoginPage.css';  // 共用登入頁面的樣式

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    line_id: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 驗證密碼
    if (formData.password !== formData.confirmPassword) {
      setError('密碼不一致');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          phone: formData.phone,
          line_id: formData.line_id
        }),
      });

      const data = await response.json();
      if (response.ok) {
        // 註冊成功後直接登入
        localStorage.setItem('token', data.access_token);
        navigate('/profile');
      } else {
        setError(data.error || '註冊失敗');
      }
    } catch (err) {
      setError('伺服器錯誤，請稍後再試');
    }
  };

  return (
    <div className="login-page">
      <h2>註冊帳號</h2>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label>姓名:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            maxLength={100}
          />
        </div>
        <div className="form-group">
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>密碼:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            minLength={6}
          />
        </div>
        <div className="form-group">
          <label>確認密碼:</label>
          <input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            minLength={6}
          />
        </div>
        <div className="form-group">
          <label>手機號碼:</label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            pattern="09[0-9]{8}"
            maxLength={10}
            placeholder="09xxxxxxxx"
          />
        </div>
        <div className="form-group">
          <label>Line ID:</label>
          <input
            type="text"
            name="line_id"
            value={formData.line_id}
            onChange={handleChange}
            maxLength={50}
          />
        </div>
        {error && <p className="error">{error}</p>}
        <button type="submit">註冊</button>
      </form>
      <p>
        已經有帳號？<Link to="/login">登入</Link>
      </p>
    </div>
  );
};

export default Register;