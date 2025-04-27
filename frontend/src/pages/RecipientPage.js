import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import RecipientForm from '../components/RecipientForm';
import '../styles/RecipientPage.css';

const RecipientPage = () => {
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingRecipient, setEditingRecipient] = useState(null);

  useEffect(() => {
    fetchRecipients();
  }, []);

  const fetchRecipients = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const response = await fetch('http://localhost:5000/api/recipients', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setRecipients(data);
    } catch (err) {
      console.error('Failed to fetch recipients:', err);
      setError('載入收貨人資料失敗');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('確定要刪除這個收貨人資料嗎？')) return;
    
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://localhost:5000/api/recipients/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (response.ok) {
        setRecipients(recipients.filter(r => r.id !== id));
      } else {
        const data = await response.json();
        setError(data.error || '刪除失敗');
      }
    } catch (err) {
      console.error('Failed to delete recipient:', err);
      setError('刪除失敗');
    }
  };

  const handleEdit = (recipient) => {
    setEditingRecipient(recipient);
    setShowForm(true);
  };

  const handleFormSubmit = async (formData) => {
    const token = localStorage.getItem('token');
    try {
      const url = editingRecipient
        ? `http://localhost:5000/api/recipients/${editingRecipient.id}`
        : 'http://localhost:5000/api/recipients';
      
      const method = editingRecipient ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (response.ok) {
        await fetchRecipients();
        setShowForm(false);
        setEditingRecipient(null);
      } else {
        setError(data.error || '儲存失敗');
      }
    } catch (err) {
      console.error('Failed to save recipient:', err);
      setError('儲存失敗');
    }
  };

  return (
    <div className="recipient-page">
      <h2>收貨人管理</h2>
      {error && <div className="error-message">{error}</div>}
      
      {!showForm && (
        <button 
          className="add-button"
          onClick={() => setShowForm(true)}
          disabled={recipients.length >= 5}
        >
          {recipients.length >= 5 ? '已達到5組上限' : '新增收貨人'}
        </button>
      )}

      {showForm && (
        <RecipientForm
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingRecipient(null);
          }}
          initialData={editingRecipient}
        />
      )}

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="recipient-list">
          {recipients.map((recipient) => (
            <div key={recipient.id} className="recipient-card">
              <h3>{recipient.name}</h3>
              <p>電話：{recipient.phone}</p>
              <p>地址：{recipient.address}</p>
              <div className="recipient-actions">
                <button onClick={() => handleEdit(recipient)}>編輯</button>
                <button onClick={() => handleDelete(recipient.id)}>刪除</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecipientPage;