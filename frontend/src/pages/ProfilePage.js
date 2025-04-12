import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import '../styles/ProfilePage.css';

const ProfilePage = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const response = await fetch('http://localhost:5000/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        const data = await response.json();
        setUser(data);
      } catch (err) {
        console.error('Failed to fetch profile:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <div className="profile-page">
      <h2>個人資料</h2>
      {loading ? (
        <LoadingSpinner />
      ) : !user ? (
        <p>請先登入</p>
      ) : (
        <div className="profile-info">
          <p><strong>姓名:</strong> {user.name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>角色:</strong> {user.role}</p>
          <p><strong>電話:</strong> {user.phone || '未提供'}</p>
          <p><strong>Line ID:</strong> {user.line_id || '未提供'}</p>
          <button className="edit-btn">編輯資料</button>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;