import React, { useState, useEffect } from 'react';
import { notification } from 'antd';

const ChangePasswordForm = ({ user }) => {
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
    superadmin_code: '' // 特殊驗證碼，僅 SUPERADMIN 需填寫
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // 判斷是否為 SUPERADMIN JackeyChen
  const isSuperAdmin = user && user.role === 'superadmin' && user.username === 'JackeyChen';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 驗證新密碼與確認密碼是否一致
    if (formData.new_password !== formData.confirm_password) {
      setError('新密碼與確認密碼不一致');
      return;
    }
    
    // 驗證新密碼強度
    if (formData.new_password.length < 8) {
      setError('新密碼至少需要8個字元');
      return;
    }
    
    // 若為 SUPERADMIN 且未填寫特殊驗證碼
    if (isSuperAdmin && !formData.superadmin_code) {
      setError('SUPERADMIN 帳號需要填寫特殊驗證碼');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/user/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          old_password: formData.old_password,
          new_password: formData.new_password,
          ...(isSuperAdmin && { superadmin_code: formData.superadmin_code })
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        notification.success({
          message: '成功',
          description: '密碼已成功變更'
        });
        // 清空表單
        setFormData({
          old_password: '',
          new_password: '',
          confirm_password: '',
          superadmin_code: ''
        });
      } else {
        setError(data.error || '密碼變更失敗');
      }
    } catch (err) {
      console.error('密碼變更出錯:', err);
      setError('網路錯誤，請稍後再試');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-form">
      <h3>變更密碼</h3>
      
      {isSuperAdmin && (
        <div className="superadmin-notice">
          <p className="warning">注意：SUPERADMIN 帳號變更密碼需要額外驗證</p>
          <p>僅允許一個 SUPERADMIN 帳號 (JackeyChen)</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>舊密碼</label>
          <input
            type="password"
            name="old_password"
            value={formData.old_password}
            onChange={handleChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label>新密碼</label>
          <input
            type="password"
            name="new_password"
            value={formData.new_password}
            onChange={handleChange}
            required
            minLength={8}
          />
        </div>
        
        <div className="form-group">
          <label>確認新密碼</label>
          <input
            type="password"
            name="confirm_password"
            value={formData.confirm_password}
            onChange={handleChange}
            required
            minLength={8}
          />
        </div>
        
        {isSuperAdmin && (
          <div className="form-group">
            <label>SUPERADMIN 特殊驗證碼</label>
            <input
              type="password"
              name="superadmin_code"
              value={formData.superadmin_code}
              onChange={handleChange}
              required={isSuperAdmin}
              placeholder="請輸入特殊驗證碼"
            />
            <small className="helper-text">SUPERADMIN 需要輸入特殊驗證碼才能變更密碼</small>
          </div>
        )}
        
        {error && <p className="error">{error}</p>}
        
        <button type="submit" disabled={loading}>
          {loading ? '處理中...' : '變更密碼'}
        </button>
      </form>
    </div>
  );
};

export default ChangePasswordForm;
